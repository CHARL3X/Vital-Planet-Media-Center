"""
Vital Planet Asset Hub - File Analyzer
Intelligent file classification and analysis system.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from backend.config.settings import settings

class FileAnalyzer:
    """Analyzes files and classifies them according to Vital Planet standards."""
    
    def __init__(self):
        self.classification_rules = settings.CLASSIFICATION_RULES
        self.scan_extensions = settings.SCAN_EXTENSIONS
        
    def extract_product_info(self, folder_name: str) -> Optional[Dict[str, str]]:
        """Extract product code and information from folder name."""
        pattern = self.classification_rules['product_code_pattern']
        match = re.match(pattern, folder_name)
        
        if not match:
            return None
            
        code = match.group(1)
        name = match.group(2).strip()
        
        # Clean up common formatting issues
        name = self._clean_product_name(name)
        
        # Determine category
        category = self._determine_category(name)
        
        return {
            'code': code,
            'name': name,
            'category': category
        }
    
    def classify_asset(self, file_path: Path, base_path: Path) -> Tuple[str, bool]:
        """
        Classify what type of asset this file represents.
        
        Returns:
            Tuple of (asset_type, is_current)
        """
        path_str = str(file_path).lower()
        name = file_path.name.lower()
        
        # Check if file should be included
        if not self._should_include_file(file_path):
            return "Excluded", False
        
        # Determine if it's current or archived
        is_current = self._is_current_version(path_str)
        
        # Classify asset type
        asset_type = self._classify_asset_type(path_str, name)
        
        return asset_type, is_current
    
    def _clean_product_name(self, name: str) -> str:
        """Clean and standardize product name."""
        # Remove extra whitespace and underscores
        name = re.sub(r'[_\s]+', ' ', name).strip()
        
        # Remove common prefixes if they're redundant
        prefixes_to_clean = ['Vital Planet', 'VP']
        for prefix in prefixes_to_clean:
            if name.startswith(prefix):
                name = name[len(prefix):].strip(' -_')
        
        # Standardize common abbreviations
        standardizations = {
            'FG': 'FG',  # Freeze-Dried
            'SS': 'SS',  # Shelf-Stable
            'ct': 'ct',  # Count
            'VF': 'VF',  # Vital Flora
            'IC': 'IntenseCare'
        }
        
        for old, new in standardizations.items():
            name = re.sub(rf'\b{old}\b', new, name, flags=re.IGNORECASE)
        
        return name
    
    def _determine_category(self, name: str) -> str:
        """Determine product category based on name patterns."""
        name_lower = name.lower()
        
        # Check for specific patterns in order of specificity
        
        # IntenseCare products
        if 'intensecare' in name_lower:
            if 'fg' in name_lower:
                return 'IntenseCare FG'
            elif 'ss' in name_lower:
                return 'IntenseCare SS'
            else:
                return 'IntenseCare'
        
        # Vital Flora products
        if any(term in name_lower for term in ['vf', 'vital flora']):
            if 'fg' in name_lower:
                return 'Vital Flora FG'
            elif 'ss' in name_lower:
                return 'Vital Flora SS'
            else:
                return 'Vital Flora'
        
        # Organic Flora
        if 'organic flora' in name_lower:
            return 'Organic Flora'
        
        # Amazon Kits
        if any(term in name_lower for term in ['hope', 'amazon', 'kit']):
            return 'Amazon Kits'
        
        # Digestive Health (broader category)
        digestive_keywords = [
            'omega', 'gut', 'liver', 'lax', 'fiber', 'detox', 
            'cleanse', 'digest', 'renew', 'boost', 'pure'
        ]
        if any(keyword in name_lower for keyword in digestive_keywords):
            return 'Digestive Health'
        
        return 'Other'
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the index."""
        extension = file_path.suffix.lower()
        
        # Check against known extensions
        all_extensions = set()
        for ext_group in self.scan_extensions.values():
            all_extensions.update(ext_group)
        
        if extension not in all_extensions:
            return False
        
        # Exclude system files
        system_files = {'.ds_store', 'thumbs.db', 'desktop.ini'}
        if file_path.name.lower() in system_files:
            return False
        
        # Exclude temporary files
        temp_patterns = ['.tmp', '~$', '.lock']
        if any(pattern in file_path.name.lower() for pattern in temp_patterns):
            return False
        
        return True
    
    def _is_current_version(self, path_str: str) -> bool:
        """Determine if this is a current version or archived."""
        path_lower = path_str.lower()
        
        # Files in these directories are considered archived
        archive_indicators = [
            'old versions', 'old mock-ups', 'old mock ups', 'old mockups',
            'drafts', 'archive', 'backup', 'not used', 'unused',
            'previous', 'deprecated', 'outdated', 'old links'
        ]
        
        # Check if any archive indicator is in the path
        is_archived = any(indicator in path_lower for indicator in archive_indicators)
        
        # Files in "Print Ready" directories are definitely current
        if 'print ready' in path_lower and not is_archived:
            return True
        
        # Files with DRAFT in the name are archived unless in current directories
        if 'draft' in path_lower:
            return False
        
        return not is_archived
    
    def _classify_asset_type(self, path_str: str, filename: str) -> str:
        """Classify the type of asset based on path and filename."""
        
        # Convert to lowercase for case-insensitive matching
        path_lower = path_str.lower()
        filename_lower = filename.lower()
        
        # Priority-based classification (most specific first)
        
        # 1. Print Ready - highest priority
        print_indicators = ['print ready', 'print-ready', 'printready', 'production', '/final/', 'sunset']
        if any(indicator in path_lower for indicator in print_indicators):
            return 'Print Ready'
        
        # 2. 3D Mockups - Check FIRST since PNG files in mockup directories are highest priority
        mockup_path_indicators = [
            'mock ups/3d', 'mock-ups/3d', 'mockups/3d',
            'old mock-ups', 'old mock ups', 'old mockups',
            '3d mockups, images, flatbacks, other related',
            '01 - mockups', '00 - 3d'
        ]
        
        # Check if PNG/PSD/JPG files in mockup directories
        if any(indicator in path_lower for indicator in mockup_path_indicators):
            if filename_lower.endswith(('.png', '.jpg', '.jpeg', '.psd')):
                return '3D Mockup'
        
        # Additional check for PNG files in any directory containing "mock"
        if 'mock' in path_lower and filename_lower.endswith(('.png', '.jpg', '.jpeg')):
            return '3D Mockup'
        
        # 3. Label Art - check for label-specific patterns
        label_indicators = [
            'label', '-l', '_l_', '19207l', '19207-l',  # File naming patterns
            '/labels/', 'part 1 label', 'part 2 label'   # Path patterns
        ]
        if any(indicator in path_lower or indicator in filename_lower for indicator in label_indicators):
            return 'Label Art'
        
        # 4. Box Art - check for box-specific patterns
        box_indicators = [
            'box', '-b', '_b_', '19207b', '19207-b',     # File naming patterns
            '/box/', 'packaging'                          # Path patterns
        ]
        if any(indicator in path_lower or indicator in filename_lower for indicator in box_indicators):
            return 'Box Art'
        
        # 5. Archive/Draft files
        archive_indicators = ['old', 'draft', 'archive', 'backup', 'not used', 'previous']
        if any(indicator in path_lower for indicator in archive_indicators):
            return 'Archive'
        
        # 6. Templates
        template_indicators = ['template', 'dieline', 'die line']
        if any(indicator in path_lower for indicator in template_indicators):
            return 'Template'
        
        # 7. Documentation
        doc_indicators = ['report', 'change', 'spec', 'instruction', '.docx', '.txt', '.pdf']
        if any(indicator in filename_lower for indicator in doc_indicators):
            return 'Documentation'
        
        # 8. Check file extensions for better classification
        file_ext = filename_lower.split('.')[-1] if '.' in filename_lower else ''
        
        if file_ext in ['png', 'jpg', 'jpeg']:
            # Images that aren't already classified 
            # In VP context, most PNGs are either 3D mockups or reference images
            # Default to 3D Mockup for PNG files as these are commonly the product visuals needed
            return '3D Mockup'
        
        if file_ext in ['ai', 'psd']:
            # Design files that aren't already classified
            if 'box' in filename_lower or 'packaging' in filename_lower:
                return 'Box Art'
            elif 'label' in filename_lower:
                return 'Label Art'
            else:
                return 'Box Art'  # Default for design files
        
        # Default classification
        return 'Other'
    
    def analyze_directory_structure(self, directory: Path) -> Dict[str, any]:
        """Analyze the overall structure of a product directory."""
        structure_info = {
            'has_mockups': False,
            'has_print_ready': False,
            'has_current_files': False,
            'has_archive': False,
            'subfolder_count': 0,
            'file_count': 0,
            'common_patterns': []
        }
        
        try:
            # Count subfolders
            subfolders = [d for d in directory.iterdir() if d.is_dir()]
            structure_info['subfolder_count'] = len(subfolders)
            
            # Analyze subfolder names for patterns
            folder_names = [d.name.lower() for d in subfolders]
            
            # Check for common patterns
            if any('mock' in name or '3d' in name for name in folder_names):
                structure_info['has_mockups'] = True
                structure_info['common_patterns'].append('mockups')
            
            if any('print' in name for name in folder_names):
                structure_info['has_print_ready'] = True
                structure_info['common_patterns'].append('print_ready')
            
            if any('old' in name or 'archive' in name for name in folder_names):
                structure_info['has_archive'] = True
                structure_info['common_patterns'].append('archive')
            
            # Count total files
            structure_info['file_count'] = sum(
                1 for f in directory.rglob('*') if f.is_file()
            )
            
        except (OSError, PermissionError):
            # Handle directories that can't be accessed
            pass
        
        return structure_info
    
    def get_file_insights(self, file_path: Path) -> Dict[str, any]:
        """Get detailed insights about a specific file."""
        insights = {
            'is_design_file': False,
            'is_production_ready': False,
            'estimated_purpose': 'unknown',
            'quality_indicators': []
        }
        
        extension = file_path.suffix.lower()
        name_lower = file_path.name.lower()
        
        # Determine if it's a design file
        design_extensions = {'.ai', '.psd', '.indd'}
        insights['is_design_file'] = extension in design_extensions
        
        # Check for production readiness indicators
        production_indicators = ['final', 'print', 'production', 'ready']
        insights['is_production_ready'] = any(
            indicator in name_lower for indicator in production_indicators
        )
        
        # Estimate purpose
        if 'mock' in name_lower or '3d' in name_lower:
            insights['estimated_purpose'] = 'visualization'
        elif 'label' in name_lower:
            insights['estimated_purpose'] = 'labeling'
        elif 'box' in name_lower:
            insights['estimated_purpose'] = 'packaging'
        elif extension == '.pdf':
            insights['estimated_purpose'] = 'documentation'
        
        # Quality indicators
        if 'high' in name_lower or 'hd' in name_lower:
            insights['quality_indicators'].append('high_quality')
        
        if 'draft' in name_lower:
            insights['quality_indicators'].append('draft')
        
        return insights