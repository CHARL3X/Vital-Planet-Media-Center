#!/usr/bin/env python3
"""
Test script for multi-directory scanning functionality
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports  
sys.path.append(str(Path(__file__).parent.parent))

from backend.scanner.asset_scanner import AssetScanner

def test_multi_directory_scan():
    print("🌱 Testing Multi-Directory Asset Scanner")
    print("=" * 50)
    
    try:
        # Test Human + Pet scanning
        print("Testing Human + Pet scanning...")
        scanner = AssetScanner(scan_mode="all")
        
        # Scan specific directories
        directories = ['human_current', 'pet_current']
        results = scanner.scan_multiple_directories(directories)
        
        print(f"✅ Multi-scan completed!")
        print(f"📦 Total Products: {results.metadata.total_products}")
        print(f"📁 Total Assets: {results.metadata.total_assets:,}")
        print(f"⏱️  Duration: {results.metadata.scan_duration:.2f} seconds")
        
        # Show breakdown by product line
        human_products = [p for p in results.products.values() if p.product_line == "Human"]
        pet_products = [p for p in results.products.values() if p.product_line == "Pet"]
        
        print(f"\n📊 Breakdown:")
        print(f"   🧑 Human Products: {len(human_products)}")
        print(f"   🐕 Pet Products: {len(pet_products)}")
        
        # Save test results to temporary file (don't clutter project)
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            results.save_to_file(Path(tmp.name))
            print(f"💾 Test results saved to temporary file")
            # Clean up test file
            Path(tmp.name).unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-scan failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pet_only_scan():
    print("\n🐕 Testing Pet-Only Scanning")
    print("=" * 30)
    
    try:
        scanner = AssetScanner(scan_mode="pet_current")
        results = scanner.scan_multiple_directories(['pet_current'])
        
        print(f"✅ Pet scan completed!")
        print(f"📦 Pet Products: {results.metadata.total_products}")
        print(f"📁 Pet Assets: {results.metadata.total_assets:,}")
        
        # Show some pet product examples
        pet_products = list(results.products.values())[:5]
        print(f"\n🔍 Sample Pet Products:")
        for product in pet_products:
            print(f"   {product.code}: {product.name[:40]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Pet scan failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_multi_directory_scan()
    success2 = test_pet_only_scan()
    
    if success1 and success2:
        print(f"\n🎉 All tests passed! Multi-directory scanning is working.")
    else:
        print(f"\n⚠️  Some tests failed. Check the logs above.")