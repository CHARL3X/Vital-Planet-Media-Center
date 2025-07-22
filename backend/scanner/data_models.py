"""
Vital Planet Asset Hub - Data Models
Data structures for asset and product information.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import json
import re

@dataclass
class AssetInfo:
    """Represents a single asset file."""
    name: str
    path: str
    relative_path: str
    type: str
    is_current: bool
    extension: str
    size: int
    modified: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.modified, datetime):
            self.modified = self.modified.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_file(cls, file_path: Path, base_path: Path, asset_type: str, is_current: bool) -> 'AssetInfo':
        """Create AssetInfo from file path."""
        try:
            stat = file_path.stat()
            return cls(
                name=file_path.name,
                path=str(file_path),
                relative_path=str(file_path.relative_to(base_path)),
                type=asset_type,
                is_current=is_current,
                extension=file_path.suffix.lower(),
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
            )
        except (OSError, ValueError) as e:
            # Handle files that can't be accessed
            return cls(
                name=file_path.name,
                path=str(file_path),
                relative_path=str(file_path.relative_to(base_path)) if base_path else str(file_path),
                type=asset_type,
                is_current=is_current,
                extension=file_path.suffix.lower() if file_path.suffix else '',
                size=0,
                modified=None
            )

@dataclass
class AssetGroup:
    """Represents a group of related asset files (e.g., PNG/PSD/JPG of same mockup)."""
    base_name: str
    primary_asset: AssetInfo  # The main display asset (usually PNG)
    related_assets: List[AssetInfo]  # All assets in the group
    asset_type: str
    is_current: bool
    
    @property
    def total_assets(self) -> int:
        """Total number of assets in this group."""
        return len(self.related_assets)
    
    @property
    def available_formats(self) -> List[str]:
        """List of available file formats in this group."""
        return sorted(list(set(asset.extension.replace('.', '').upper() 
                                for asset in self.related_assets)))
    
    def get_asset_by_extension(self, extension: str) -> Optional[AssetInfo]:
        """Get asset by file extension."""
        ext = extension.lower().replace('.', '')
        for asset in self.related_assets:
            if asset.extension.replace('.', '').lower() == ext:
                return asset
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'base_name': self.base_name,
            'primary_asset': self.primary_asset.to_dict(),
            'related_assets': [asset.to_dict() for asset in self.related_assets],
            'asset_type': self.asset_type,
            'is_current': self.is_current,
            'total_assets': self.total_assets,
            'available_formats': self.available_formats,
            'is_grouped': True  # Flag to indicate this is a grouped asset
        }

@dataclass
class ProductInfo:
    """Represents a product with its assets."""
    code: str
    name: str
    category: str
    folder_path: str
    assets: List[AssetInfo]
    directory_source: str = "human_current"  # Which directory this came from
    product_line: str = "Human"  # Human or Pet
    status: str = "Current"  # Current or Work in Progress
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'code': self.code,
            'name': self.name,
            'category': self.category,
            'folder_path': self.folder_path,
            'directory_source': self.directory_source,
            'product_line': self.product_line,
            'status': self.status,
            'assets': [asset.to_dict() for asset in self.assets]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductInfo':
        """Create ProductInfo from dictionary."""
        assets = [AssetInfo(**asset_data) for asset_data in data.get('assets', [])]
        return cls(
            code=data['code'],
            name=data['name'],
            category=data['category'],
            folder_path=data['folder_path'],
            directory_source=data.get('directory_source', 'human_current'),
            product_line=data.get('product_line', 'Human'),
            status=data.get('status', 'Current'),
            assets=assets
        )
    
    def get_asset_counts(self) -> Dict[str, int]:
        """Get count of assets by type."""
        counts = {}
        for asset in self.assets:
            counts[asset.type] = counts.get(asset.type, 0) + 1
        return counts
    
    def get_current_assets(self) -> List[AssetInfo]:
        """Get only current (non-archived) assets."""
        return [asset for asset in self.assets if asset.is_current]
    
    def get_archived_assets(self) -> List[AssetInfo]:
        """Get only archived assets."""
        return [asset for asset in self.assets if not asset.is_current]
    
    def group_3d_mockups(self) -> List[AssetGroup]:
        """
        Group 3D mockup assets by base filename to reduce UI clutter.
        Groups files like 'Critical Liver Care Box.png/.psd/.jpg' into one item.
        """
        # Only group 3D Mockups
        mockup_assets = [asset for asset in self.assets if asset.type == '3D Mockup']
        
        if not mockup_assets:
            return []
        
        # Group by base filename (without extension)
        groups = defaultdict(list)
        for asset in mockup_assets:
            # Remove extension and common suffixes to get base name
            base_name = self._get_base_filename(asset.name)
            groups[base_name].append(asset)
        
        # Create AssetGroup objects
        asset_groups = []
        for base_name, assets in groups.items():
            if len(assets) > 1:  # Only group if multiple assets
                # Prioritize PNG as primary, then JPG, then PSD
                primary_asset = self._select_primary_asset(assets)
                asset_groups.append(AssetGroup(
                    base_name=base_name,
                    primary_asset=primary_asset,
                    related_assets=assets,
                    asset_type='3D Mockup',
                    is_current=primary_asset.is_current
                ))
            else:
                # Single asset, don't group
                continue
                
        return asset_groups
    
    def _get_base_filename(self, filename: str) -> str:
        """Extract base filename without extension and common suffixes."""
        # Remove file extension
        base = Path(filename).stem
        
        # Remove common 3D mockup suffixes that might cause grouping issues
        # But keep the meaningful part
        base = re.sub(r'\s*\(?\d+\)?$', '', base)  # Remove trailing numbers in parentheses
        
        return base.strip()
    
    def _select_primary_asset(self, assets: List[AssetInfo]) -> AssetInfo:
        """Select the primary asset for display (prioritize PNG > JPG > PSD)."""
        # Priority order for display
        priority_extensions = ['.png', '.jpg', '.jpeg', '.psd', '.ai']
        
        for ext in priority_extensions:
            for asset in assets:
                if asset.extension.lower() == ext:
                    return asset
        
        # Fallback to first asset if no priority match
        return assets[0]

@dataclass
class ScanMetadata:
    """Metadata about a scan operation."""
    scan_date: str
    source_directory: str
    total_products: int
    total_assets: int
    scan_duration: float
    version: str = "1.0.0"
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.scan_date, datetime):
            self.scan_date = self.scan_date.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class AssetIndex:
    """Complete asset index with metadata and products."""
    metadata: ScanMetadata
    products: Dict[str, ProductInfo]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metadata': self.metadata.to_dict(),
            'products': {code: product.to_dict() for code, product in self.products.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetIndex':
        """Create AssetIndex from dictionary."""
        metadata = ScanMetadata(**data['metadata'])
        products = {
            code: ProductInfo.from_dict(product_data)
            for code, product_data in data.get('products', {}).items()
        }
        return cls(metadata=metadata, products=products)
    
    def save_to_file(self, file_path: Path) -> None:
        """Save index to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'AssetIndex':
        """Load index from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        return list(set(product.category for product in self.products.values()))
    
    def get_asset_types(self) -> List[str]:
        """Get list of unique asset types."""
        asset_types = set()
        for product in self.products.values():
            asset_types.update(asset.type for asset in product.assets)
        return list(asset_types)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        category_counts = {}
        asset_type_counts = {}
        total_files = 0
        
        for product in self.products.values():
            # Count by category
            category_counts[product.category] = category_counts.get(product.category, 0) + 1
            
            # Count by asset type
            for asset in product.assets:
                asset_type_counts[asset.type] = asset_type_counts.get(asset.type, 0) + 1
                total_files += 1
        
        return {
            'total_products': len(self.products),
            'total_files': total_files,
            'categories': category_counts,
            'asset_types': asset_type_counts,
            'scan_date': self.metadata.scan_date,
            'source_directory': self.metadata.source_directory
        }
    
    def create_grouped_version(self) -> 'AssetIndex':
        """
        Create a version of this index with 3D mockups grouped by similar filenames.
        This reduces UI clutter while preserving all asset access.
        """
        grouped_products = {}
        
        for code, product in self.products.items():
            # Create grouped assets for this product
            grouped_assets = []
            ungrouped_assets = []
            
            # Get 3D mockup groups
            mockup_groups = product.group_3d_mockups()
            
            # Track which assets are already grouped
            grouped_asset_names = set()
            for group in mockup_groups:
                for asset in group.related_assets:
                    grouped_asset_names.add(asset.name)
            
            # Add grouped 3D mockups
            for group in mockup_groups:
                # Convert AssetGroup to a dict that looks like AssetInfo for UI compatibility
                group_dict = group.to_dict()
                # Add fields that UI expects from AssetInfo
                group_dict.update({
                    'name': group.primary_asset.name,
                    'path': group.primary_asset.path,
                    'relative_path': group.primary_asset.relative_path,
                    'extension': group.primary_asset.extension,
                    'size': sum(asset.size for asset in group.related_assets),
                    'modified': group.primary_asset.modified
                })
                grouped_assets.append(group_dict)
            
            # Add all non-3D-mockup assets and ungrouped 3D mockups
            for asset in product.assets:
                if asset.name not in grouped_asset_names:
                    ungrouped_assets.append(asset)
            
            # Create new product with mixed grouped and ungrouped assets
            grouped_products[code] = ProductInfo(
                code=product.code,
                name=product.name,
                category=product.category,
                folder_path=product.folder_path,
                directory_source=product.directory_source,
                product_line=product.product_line,
                status=product.status,
                assets=ungrouped_assets  # Keep ungrouped as AssetInfo objects
            )
            
            # Store grouped info separately for UI processing
            grouped_products[code]._grouped_assets = grouped_assets
        
        # Create new index with grouped data
        return AssetIndex(
            metadata=self.metadata,
            products=grouped_products
        )

# Utility functions for data validation and processing

def validate_product_code(code: str) -> bool:
    """Validate that a product code follows the expected format."""
    return code.isdigit() and len(code) == 5

def clean_product_name(name: str) -> str:
    """Clean and standardize product name."""
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Remove redundant prefixes if they exist
    prefixes_to_remove = ['Vital Planet', 'VP']
    for prefix in prefixes_to_remove:
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
    
    return name

def categorize_by_keywords(name: str, category_rules: Dict[str, List[str]]) -> str:
    """Categorize product based on name keywords."""
    name_lower = name.lower()
    
    for category, keywords in category_rules.items():
        if all(keyword.lower() in name_lower for keyword in keywords):
            return category
        elif any(keyword.lower() in name_lower for keyword in keywords):
            # Partial match - need more specific logic
            continue
    
    return "Other"