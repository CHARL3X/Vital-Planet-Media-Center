"""
Vital Planet Asset Hub - Flask Server
Web server for the asset dashboard.
"""

import os
import json
import sys
import subprocess
import signal
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request, send_file, abort
from urllib.parse import unquote
from PIL import Image
import io

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from backend.config.settings import get_config
    from backend.scanner.asset_scanner import AssetScanner
    config = get_config(os.getenv('VP_ENV', 'production'))
except ImportError:
    # Fallback configuration if modules don't import
    class Config:
        APP_NAME = "Vital Planet Asset Hub"
        VERSION = "1.0.0"
        COMPANY = "Vital Planet"
        PRIMARY_COLOR = "#732d83"
        SECONDARY_COLOR = "#9c4dcc"
        ACCENT_COLOR = "#e1bee7"
        HOST = "localhost"
        PORT = 8080
        DEBUG = False
    config = Config()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Initialize Flask app with correct paths
app = Flask(__name__, static_folder=str(PROJECT_ROOT), static_url_path='')

@app.route('/')
def index():
    """Serve the main dashboard page."""
    try:
        return send_from_directory(str(PROJECT_ROOT), 'index.html')
    except Exception as e:
        return f"Error serving index.html: {e}", 500

@app.route('/timeline')
def timeline():
    """Serve the timeline page."""
    try:
        return send_from_directory(str(PROJECT_ROOT), 'timeline.html')
    except Exception as e:
        return f"Error serving timeline.html: {e}", 500

@app.route('/styles.css')
def serve_css():
    """Serve CSS file."""
    try:
        return send_from_directory(str(PROJECT_ROOT), 'styles.css')
    except Exception as e:
        return f"Error serving styles.css: {e}", 500

@app.route('/dashboard.js')
def serve_js():
    """Serve JavaScript file."""
    try:
        return send_from_directory(str(PROJECT_ROOT), 'dashboard.js')
    except Exception as e:
        return f"Error serving dashboard.js: {e}", 500

@app.route('/assets_index.json')
def get_assets_index():
    """Serve the assets index JSON."""
    try:
        index_path = PROJECT_ROOT / 'assets_index.json'
        if not index_path.exists():
            return jsonify({
                'error': 'Assets index not found',
                'message': 'Please run the asset scanner first: ./scripts/scan_assets.sh'
            }), 404
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to load assets index',
            'message': str(e)
        }), 500

@app.route('/api/config')
def get_config_info():
    """Get configuration information for the frontend."""
    return jsonify({
        'app_name': config.APP_NAME,
        'version': config.VERSION,
        'company': config.COMPANY,
        'primary_color': config.PRIMARY_COLOR,
        'secondary_color': config.SECONDARY_COLOR,
        'accent_color': config.ACCENT_COLOR
    })

@app.route('/refresh-assets', methods=['POST'])
@app.route('/api/refresh-assets', methods=['POST'])
@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a new asset scan with multi-directory support."""
    try:
        # Use multi-directory scanner to scan all directories
        scanner = AssetScanner(scan_mode="all")
        asset_index = scanner.scan_multiple_directories()
        scanner.save_index(asset_index)
        
        return jsonify({
            'success': True,
            'message': 'Multi-directory asset scan completed successfully',
            'results': {
                'products': asset_index.metadata.total_products,
                'assets': asset_index.metadata.total_assets,
                'duration': asset_index.metadata.scan_duration,
                'scan_date': asset_index.metadata.scan_date
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Multi-directory scan failed',
            'message': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics."""
    try:
        index_path = PROJECT_ROOT / 'assets_index.json'
        if not index_path.exists():
            return jsonify({'error': 'No data available'}), 404
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        products = data.get('products', {})
        
        # Calculate additional stats
        categories = {}
        asset_types = {}
        
        for product in products.values():
            category = product.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            for asset in product.get('assets', []):
                asset_type = asset.get('type', 'Unknown')
                asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
        
        return jsonify({
            'total_products': metadata.get('total_products', 0),
            'total_assets': metadata.get('total_assets', 0),
            'scan_date': metadata.get('scan_date', 'Unknown'),
            'categories': categories,
            'asset_types': asset_types,
            'source_directory': metadata.get('source_directory', 'Unknown')
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500

@app.route('/api/file')
def serve_file():
    """Serve files from local filesystem."""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        # Decode the path
        file_path = unquote(file_path)
        
        # Security check - ensure file exists and is accessible
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send the file
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({'error': f'Failed to serve file: {str(e)}'}), 500

@app.route('/api/thumbnail')
def serve_thumbnail():
    """Generate and serve thumbnails for images."""
    file_path = request.args.get('path')
    size = int(request.args.get('size', 200))
    
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        # Decode the path
        file_path = unquote(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if it's an image file
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            return jsonify({'error': 'File is not an image'}), 400
        
        # Generate thumbnail
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Save to bytes
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=85)
            img_io.seek(0)
            
            return send_file(img_io, mimetype='image/jpeg')
            
    except Exception as e:
        return jsonify({'error': f'Failed to generate thumbnail: {str(e)}'}), 500

@app.route('/api/download')
def download_file():
    """Download files with proper headers."""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        # Decode the path
        file_path = unquote(file_path)
        
        # Security check
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get filename
        filename = os.path.basename(file_path)
        
        # Send file as download
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    index_exists = (PROJECT_ROOT / 'assets_index.json').exists()
    return jsonify({
        'status': 'healthy',
        'app': config.APP_NAME,
        'version': config.VERSION,
        'index_exists': index_exists,
        'project_root': str(PROJECT_ROOT)
    })

@app.route('/api/timeline')
def get_timeline():
    """Get timeline data showing chronological asset activity."""
    try:
        index_path = PROJECT_ROOT / 'assets_index.json'
        if not index_path.exists():
            return jsonify({'error': 'No data available'}), 404
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data.get('products', {})
        timeline_events = []
        
        # Extract all asset modification events with enhanced temporal data
        for product_code, product in products.items():
            for asset in product.get('assets', []):
                if asset.get('modified'):
                    # Determine the most meaningful timestamp for this asset
                    primary_date = asset['modified']  # Default to filesystem date
                    date_source = 'filesystem'
                    
                    # If we have high-confidence filename date, consider using it
                    if (asset.get('best_project_date') and 
                        asset['best_project_date'].get('confidence', 0) > 0.8):
                        # Only use filename date if it's very recent or filesystem date is old
                        fs_date = datetime.fromisoformat(asset['modified'].replace('Z', '+00:00'))
                        days_old = (datetime.now() - fs_date).days
                        if days_old > 90:  # If filesystem date is old, filename might be better
                            primary_date = asset['best_project_date']['date']
                            date_source = f"filename ({asset['best_project_date']['pattern_type']})"
                    
                    timeline_events.append({
                        'date': primary_date,
                        'date_source': date_source,
                        'product_code': product_code,
                        'product_name': product['name'],
                        'product_line': product.get('product_line', 'Human'),
                        'status': product.get('status', 'Current'),
                        'asset_name': asset['name'],
                        'asset_type': asset['type'],
                        'file_extension': asset.get('extension', ''),
                        'file_size': asset.get('size', 0),
                        'is_current': asset.get('is_current', True),
                        'relative_path': asset.get('relative_path', ''),
                        'full_path': asset.get('path', ''),
                        # Enhanced temporal data
                        'activity_score': asset.get('activity_score', 0),
                        'is_recent_work': asset.get('is_recent_work', False),
                        'filesystem_date': asset['modified'],
                        'filename_dates': asset.get('filename_dates', []),
                        'best_project_date': asset.get('best_project_date')
                    })
        
        # Sort by date (newest first)
        timeline_events.sort(key=lambda x: x['date'], reverse=True)
        
        # Add grouped assets if they exist
        for product_code, product in products.items():
            grouped_assets = product.get('_grouped_assets', [])
            for group in grouped_assets:
                if group.get('modified'):
                    timeline_events.append({
                        'date': group['modified'],
                        'product_code': product_code,
                        'product_name': product['name'],
                        'product_line': product.get('product_line', 'Human'),
                        'status': product.get('status', 'Current'),
                        'asset_name': group.get('base_name', group.get('name', 'Grouped Asset')),
                        'asset_type': group.get('type', group.get('asset_type', 'Unknown')),
                        'file_extension': group.get('extension', ''),
                        'file_size': group.get('size', 0),
                        'is_current': group.get('is_current', True),
                        'relative_path': group.get('relative_path', ''),
                        'full_path': group.get('path', ''),
                        'is_grouped': True,
                        'total_assets': group.get('total_assets', 0),
                        'available_formats': group.get('available_formats', [])
                    })
        
        # Re-sort after adding grouped assets
        timeline_events.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'total_events': len(timeline_events),
            'events': timeline_events,
            'scan_date': data.get('metadata', {}).get('scan_date')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate timeline',
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found', 
        'message': f'The requested resource was not found. Available routes: /, /api/health, /api/stats, /assets_index.json'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

def kill_existing_servers(port=8080):
    """Kill any existing servers running on the specified port."""
    try:
        # Use lsof to find processes using the port
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"⚠️  Found existing processes on port {port}: {pids}")
            
            for pid in pids:
                if pid.strip():
                    try:
                        # Try graceful kill first
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"🛑 Sent SIGTERM to PID {pid}")
                    except (OSError, ValueError):
                        pass
            
            # Wait a moment for graceful shutdown
            time.sleep(2)
            
            # Check if any processes are still running and force kill
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                remaining_pids = result.stdout.strip().split('\n')
                print(f"🔥 Force killing remaining processes: {remaining_pids}")
                
                for pid in remaining_pids:
                    if pid.strip():
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                            print(f"💥 Sent SIGKILL to PID {pid}")
                        except (OSError, ValueError):
                            pass
            
            print(f"✅ Port {port} cleared successfully")
        else:
            print(f"✅ Port {port} is available")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not check/clear port {port}: {e}")
        print("Continuing with server startup...")

def main():
    """Main server entry point."""
    print(f"🌱 Starting {config.APP_NAME} v{config.VERSION}")
    
    # Auto-kill existing servers on the port
    kill_existing_servers(config.PORT)
    
    print(f"🏠 Company: {config.COMPANY}")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    print(f"🌐 Server: http://{config.HOST}:{config.PORT}")
    print(f"🎨 Theme: {config.PRIMARY_COLOR}")
    
    # Check if files exist
    files_to_check = ['index.html', 'styles.css', 'dashboard.js', 'assets_index.json']
    for file_name in files_to_check:
        file_path = PROJECT_ROOT / file_name
        status = "✅" if file_path.exists() else "❌"
        print(f"{status} {file_name}: {file_path}")
    
    try:
        # Start the Flask development server
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()