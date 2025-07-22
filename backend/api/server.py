"""
Vital Planet Asset Hub - Flask Server
Web server for the asset dashboard.
"""

import os
import json
import sys
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request

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

def main():
    """Main server entry point."""
    print(f"🌱 Starting {config.APP_NAME} v{config.VERSION}")
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