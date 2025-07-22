"""
Vital Planet Asset Hub - Modular Asset Scanner
Enhanced version with proper architecture and error handling.
"""

import os
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import our modules
from .data_models import AssetInfo, ProductInfo, ScanMetadata, AssetIndex
from .file_analyzer import FileAnalyzer
from ..config.settings import settings

class AssetScanner:
    """Professional asset scanning engine for Vital Planet packaging assets."""
    
    def __init__(self, source_dir: Optional[str] = None, output_file: Optional[str] = None, scan_mode: str = "human_current"):
        self.base_dir = Path(source_dir or settings.DEFAULT_ASSET_BASE)
        self.scan_mode = scan_mode
        self.source_dir = self._get_source_directory()
        self.output_file = output_file or "assets_index.json"
        self.analyzer = FileAnalyzer()
        
        # Track which directories we're scanning
        self.scan_directories = []
        
        # Setup logging
        self._setup_logging()
        
        # Scan statistics
        self.stats = {
            'products_processed': 0,
            'files_scanned': 0,
            'errors_encountered': 0,
            'start_time': None,
            'end_time': None
        }
        
    def _get_source_directory(self) -> Path:
        """Get the appropriate source directory based on scan mode."""
        if self.scan_mode == "all":
            return self.base_dir
        elif self.scan_mode in settings.SCAN_DIRECTORIES:
            return self.base_dir / settings.SCAN_DIRECTORIES[self.scan_mode]
        else:
            # Default to human current
            return self.base_dir / settings.SCAN_DIRECTORIES["human_current"]
    
    def _setup_logging(self):
        """Configure logging for the scanner."""
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format=settings.LOG_FORMAT,
            handlers=[
                logging.FileHandler(f"logs/{settings.LOG_FILE}"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def scan_multiple_directories(self, directories: List[str] = None) -> AssetIndex:
        """
        Scan multiple directories and build comprehensive asset index.
        
        Args:
            directories: List of directory keys to scan (e.g., ['human_current', 'pet_current'])
                        If None, scans based on scan_mode
        """
        if directories is None:
            if self.scan_mode == "all":
                directories = list(settings.SCAN_DIRECTORIES.keys())
            else:
                directories = [self.scan_mode]
        
        self.logger.info(f"Starting multi-directory scan: {directories}")
        self.stats['start_time'] = time.time()
        
        all_products = {}
        
        for dir_key in directories:
            if dir_key not in settings.SCAN_DIRECTORIES:
                self.logger.warning(f"Unknown directory key: {dir_key}")
                continue
                
            dir_path = self.base_dir / settings.SCAN_DIRECTORIES[dir_key]
            if not dir_path.exists():
                self.logger.warning(f"Directory does not exist: {dir_path}")
                continue
                
            self.logger.info(f"Scanning directory: {dir_path}")
            products = self._scan_single_directory(dir_path, dir_key)
            
            # Merge products, adding directory context
            for code, product in products.items():
                if code in all_products:
                    # Handle duplicate product codes across directories
                    self.logger.warning(f"Duplicate product code {code} found in multiple directories")
                    # Could merge or rename here
                
                # Add directory context to product
                product.directory_source = dir_key
                product.product_line = "Human" if "human" in dir_key else "Pet"
                product.status = "Current" if "current" in dir_key else "Work in Progress"
                
                all_products[code] = product
        
        # Create scan metadata
        self.stats['end_time'] = time.time()
        scan_duration = self.stats['end_time'] - self.stats['start_time']
        
        metadata = ScanMetadata(
            scan_date=datetime.now().isoformat(),
            source_directory=str(self.base_dir),
            total_products=len(all_products),
            total_assets=sum(len(p.assets) for p in all_products.values()),
            scan_duration=scan_duration,
            version=settings.VERSION if hasattr(settings, 'VERSION') else "1.0.0"
        )
        
        self.logger.info(f"Multi-directory scan completed in {scan_duration:.2f} seconds")
        self.logger.info(f"Total: {metadata.total_products} products with {metadata.total_assets} assets")
        
        return AssetIndex(metadata=metadata, products=all_products)
    
    def _scan_single_directory(self, directory: Path, dir_key: str) -> Dict[str, ProductInfo]:
        """Scan a single directory and return products."""
        products = {}
        
        try:
            # Get all product directories
            product_dirs = [
                item for item in directory.iterdir() 
                if item.is_dir() and not item.name.startswith('.')
            ]
            
            # Process directories concurrently
            with ThreadPoolExecutor(max_workers=settings.CONCURRENT_THREADS) as executor:
                future_to_dir = {
                    executor.submit(self._process_product_directory, prod_dir, dir_key): prod_dir
                    for prod_dir in product_dirs
                }
                
                for future in as_completed(future_to_dir):
                    prod_dir = future_to_dir[future]
                    try:
                        product_info = future.result()
                        if product_info:
                            products[product_info.code] = product_info
                            self.stats['products_processed'] += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error processing {prod_dir.name}: {e}")
                        self.stats['errors_encountered'] += 1
                        
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            
        return products

    def scan_directory(self) -> AssetIndex:
        """
        Scan the packaging directory and build comprehensive asset index.
        
        Returns:
            AssetIndex object containing all discovered assets
        """
        self.logger.info(f"Starting scan of {self.source_dir}")
        self.stats['start_time'] = time.time()
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        products = {}
        
        try:
            # Get all product directories
            product_dirs = [
                item for item in self.source_dir.iterdir() 
                if item.is_dir() and not item.name.startswith('.')
            ]
            
            self.logger.info(f"Found {len(product_dirs)} potential product directories")
            
            # Process directories concurrently for better performance
            with ThreadPoolExecutor(max_workers=settings.CONCURRENT_THREADS) as executor:
                future_to_dir = {
                    executor.submit(self._process_product_directory, prod_dir): prod_dir
                    for prod_dir in product_dirs
                }
                
                for future in as_completed(future_to_dir):
                    prod_dir = future_to_dir[future]
                    try:
                        product_info = future.result()
                        if product_info:
                            products[product_info.code] = product_info
                            self.stats['products_processed'] += 1
                            
                            if self.stats['products_processed'] % 10 == 0:
                                self.logger.info(f"Processed {self.stats['products_processed']} products...")
                                
                    except Exception as e:
                        self.logger.error(f"Error processing {prod_dir.name}: {e}")
                        self.stats['errors_encountered'] += 1
            
            # Create scan metadata
            self.stats['end_time'] = time.time()
            scan_duration = self.stats['end_time'] - self.stats['start_time']
            
            metadata = ScanMetadata(
                scan_date=datetime.now().isoformat(),
                source_directory=str(self.source_dir),
                total_products=len(products),
                total_assets=sum(len(p.assets) for p in products.values()),
                scan_duration=scan_duration,
                version=settings.VERSION if hasattr(settings, 'VERSION') else "1.0.0"
            )
            
            self.logger.info(f"Scan completed in {scan_duration:.2f} seconds")
            self.logger.info(f"Processed {metadata.total_products} products with {metadata.total_assets} assets")
            
            return AssetIndex(metadata=metadata, products=products)
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            raise
    
    def _process_product_directory(self, directory: Path, dir_key: str = "human_current") -> Optional[ProductInfo]:
        """Process a single product directory."""
        try:
            # Extract product information from directory name
            product_info = self.analyzer.extract_product_info(directory.name)
            if not product_info:
                self.logger.debug(f"Skipping non-product directory: {directory.name}")
                return None
            
            self.logger.debug(f"Processing product {product_info['code']}: {product_info['name']}")
            
            # Scan all files in this directory
            assets = []
            file_count = 0
            
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    file_count += 1
                    
                    # Classify the asset
                    asset_type, is_current = self.analyzer.classify_asset(file_path, directory)
                    
                    if asset_type != "Excluded":
                        asset_info = AssetInfo.from_file(file_path, directory, asset_type, is_current)
                        assets.append(asset_info)
            
            self.stats['files_scanned'] += file_count
            
            # Sort assets by type and name for consistency
            assets.sort(key=lambda x: (x.type, x.name))
            
            return ProductInfo(
                code=product_info['code'],
                name=product_info['name'],
                category=product_info['category'],
                folder_path=str(directory),
                assets=assets
            )
            
        except Exception as e:
            self.logger.error(f"Error processing directory {directory.name}: {e}")
            return None
    
    def save_index(self, asset_index: AssetIndex) -> None:
        """Save the asset index to file with proper backup management."""
        try:
            output_path = Path(self.output_file)
            
            # Create timestamped backup of existing index in backups/ directory  
            if output_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"assets_index_{timestamp}.json"
                
                # Copy to backup (don't move, in case save fails)
                shutil.copy2(output_path, backup_path)
                self.logger.info(f"Backed up existing index to {backup_path}")
                
                # Clean up old backups (keep only latest 5)
                self._cleanup_old_backups(backup_dir)
            
            # Save new index
            asset_index.save_to_file(output_path)
            self.logger.info(f"Asset index saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save index: {e}")
            raise
    
    def _cleanup_old_backups(self, backup_dir: Path, max_backups: int = 5) -> None:
        """Keep only the most recent backup files."""
        try:
            backup_files = list(backup_dir.glob("assets_index_*.json"))
            if len(backup_files) > max_backups:
                # Sort by modification time, newest first
                backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                # Remove excess files
                for old_backup in backup_files[max_backups:]:
                    old_backup.unlink()
                    self.logger.debug(f"Removed old backup: {old_backup}")
        except Exception as e:
            self.logger.warning(f"Could not cleanup old backups: {e}")
    
    def scan_and_save(self) -> Dict:
        """Convenience method to scan and save in one operation."""
        try:
            asset_index = self.scan_directory()
            self.save_index(asset_index)
            
            return {
                'success': True,
                'products': asset_index.metadata.total_products,
                'assets': asset_index.metadata.total_assets,
                'duration': asset_index.metadata.scan_duration,
                'scan_date': asset_index.metadata.scan_date
            }
            
        except Exception as e:
            self.logger.error(f"Scan and save operation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def generate_report(self, asset_index: AssetIndex) -> str:
        """Generate a detailed scan report."""
        stats = asset_index.get_summary_stats()
        
        report = f"""
        # Vital Planet Asset Hub - Scan Report
        
        ## Summary
        - **Scan Date**: {stats['scan_date']}
        - **Products**: {stats['total_products']}
        - **Files**: {stats['total_files']:,}
        - **Source**: {stats['source_directory']}
        
        ## Products by Category
        """
        
        for category, count in sorted(stats['categories'].items()):
            report += f"        - **{category}**: {count} products\n"
        
        report += "\n        ## Assets by Type\n"
        
        for asset_type, count in sorted(stats['asset_types'].items()):
            report += f"        - **{asset_type}**: {count:,} files\n"
        
        return report

def main():
    """Main entry point for command-line usage."""
    print("🌱 Vital Planet Asset Hub - Asset Scanner")
    print("=" * 50)
    
    try:
        scanner = AssetScanner()
        results = scanner.scan_and_save()
        
        if results['success']:
            print(f"✅ Scan completed successfully!")
            print(f"📦 Products: {results['products']}")
            print(f"📁 Assets: {results['assets']:,}")
            print(f"⏱️  Duration: {results['duration']:.2f} seconds")
        else:
            print(f"❌ Scan failed: {results['error']}")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Scan interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())