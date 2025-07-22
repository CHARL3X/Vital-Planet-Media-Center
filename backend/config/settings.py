"""
Vital Planet Asset Hub - Configuration Settings
Centralized configuration management for the application.
"""

import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Base configuration class."""
    
    # Application Info
    APP_NAME = "Vital Planet Asset Hub"
    VERSION = "1.0.0"
    COMPANY = "Vital Planet"
    
    # Vital Planet Branding
    PRIMARY_COLOR = "#732d83"
    SECONDARY_COLOR = "#9c4dcc"
    ACCENT_COLOR = "#e1bee7"
    
    # File Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # Default OneDrive paths - can be overridden by environment variable
    DEFAULT_ASSET_BASE = "/Users/MKTG018/Library/CloudStorage/OneDrive-VitalPlanet/Vital Planet Art/Packaging/VP PACKAGING"
    DEFAULT_ASSET_SOURCE = "/Users/MKTG018/Library/CloudStorage/OneDrive-VitalPlanet/Vital Planet Art/Packaging/VP PACKAGING/Human/Current"
    
    # Multi-directory configuration
    SCAN_DIRECTORIES = {
        'human_current': 'Human/Current',
        'human_wip': 'Human/Work in Progress', 
        'pet_current': 'Pet/Current',
        'pet_wip': 'Pet/Work in Progress'
    }
    
    @property
    def ASSET_SOURCE_PATH(self) -> str:
        """Get the asset source path from environment or default."""
        return os.getenv('VP_ASSET_SOURCE_PATH', self.DEFAULT_ASSET_SOURCE)
    
    @property
    def OUTPUT_PATH(self) -> str:
        """Get the output path for generated files."""
        return os.getenv('VP_OUTPUT_PATH', str(self.BASE_DIR / 'data'))
    
    # Server Configuration
    HOST = os.getenv('VP_HOST', 'localhost')
    PORT = int(os.getenv('VP_PORT', '8080'))
    DEBUG = os.getenv('VP_DEBUG', 'False').lower() == 'true'
    
    # Scanning Configuration
    SCAN_EXTENSIONS = {
        'images': {'.png', '.jpg', '.jpeg', '.psd', '.ai', '.pdf', '.tiff', '.tif'},
        'documents': {'.docx', '.txt', '.indd', '.doc', '.rtf', '.md'},
        'archives': {'.zip', '.rar', '.7z'},
        'videos': {'.mp4', '.mov', '.avi', '.mkv'}
    }
    
    # Asset Classification Rules
    CLASSIFICATION_RULES = {
        'product_code_pattern': r'(\d{5})[-\s]*(.+)',
        'asset_types': {
            '3D Mockup': ['mock', '3d', 'render', 'visualization'],
            'Box Art': ['box', '-b ', 'packaging'],
            'Label Art': ['label', '-l ', 'bottle'],
            'Print Ready': ['print ready', 'print-ready', 'production', 'final'],
            'Archive': ['old', 'draft', 'archive', 'backup', 'not used'],
            'Template': ['template', 'dieline', 'die line'],
            'Documentation': ['report', 'change', 'spec', 'instruction']
        },
        'categories': {
            'Vital Flora FG': ['VF', 'Vital Flora', 'FG'],
            'Vital Flora SS': ['VF', 'Vital Flora', 'SS'],
            'IntenseCare FG': ['IntenseCare', 'FG'],
            'IntenseCare SS': ['IntenseCare', 'SS'],
            'Digestive Health': ['Vital', 'Omega', 'Gut', 'Liver', 'LAX', 'Fiber', 'Detox', 'Cleanse'],
            'Organic Flora': ['Organic Flora'],
            'Amazon Kits': ['HOPE', 'Amazon']
        }
    }
    
    # Performance Settings
    MAX_SCAN_DEPTH = 10
    SCAN_TIMEOUT = 600  # 10 minutes
    MAX_FILE_SIZE_MB = 500
    CONCURRENT_THREADS = 4
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('VP_LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'vital_planet_asset_hub.log'
    
    # Cache Settings
    CACHE_ENABLED = True
    CACHE_DURATION = 3600  # 1 hour
    
    # Security Settings
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CORS_ENABLED = False  # Local use only
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'app_name': self.APP_NAME,
            'version': self.VERSION,
            'asset_source_path': self.ASSET_SOURCE_PATH,
            'output_path': self.OUTPUT_PATH,
            'host': self.HOST,
            'port': self.PORT,
            'debug': self.DEBUG,
            'primary_color': self.PRIMARY_COLOR
        }

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    CACHE_DURATION = 7200  # 2 hours

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    ASSET_SOURCE_PATH = "/tmp/test_assets"
    OUTPUT_PATH = "/tmp/test_output"

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}

def get_config(env: str = None) -> Config:
    """Get configuration for specified environment."""
    if env is None:
        env = os.getenv('VP_ENV', 'default')
    
    return config_map.get(env, Config)()

# Export default configuration
settings = get_config()