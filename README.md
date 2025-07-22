# Vital Planet Asset Hub 🌱

**One Cohesive Professional Asset Management System**

Complete multi-directory packaging asset management for Vital Planet's design workflow, scanning Human & Pet products across Current & Work in Progress directories.

## 🌟 Key Features

### Multi-Directory Asset Management
- **Comprehensive Coverage**: Scans Human + Pet product lines simultaneously
- **Status Awareness**: Tracks Current vs Work in Progress assets
- **Smart Navigation**: Multi-tier filtering by product line, status, and file type
- **Zero File Movement**: Read-only access preserves your OneDrive organization

### Intelligent Asset Classification
- **Auto-categorization**: Box Art, Label Art, Print Ready, 3D Mockups
- **Product Intelligence**: Understands Vital Planet naming conventions
- **Version Control**: Tracks current vs archived assets
- **File Type Recognition**: Optimized for AI, PSD, PNG, PDF, and more

### Professional Web Dashboard  
- **Enhanced UI**: Multi-tier navigation with Human/Pet/Both toggles
- **Smart Filtering**: Search by product code, category, file type
- **Asset Preview**: Image thumbnails and download capabilities
- **Brand Consistency**: Vital Planet colors and design language

## 🚀 Quick Start (Single Setup Process)

```bash
# 1. One-time setup (handles Python 3.13 compatibility)
./scripts/setup.sh

# 2. Generate comprehensive asset index (Human + Pet + WIP)
./scripts/scan_assets.sh  

# 3. Launch enhanced dashboard
./scripts/start_server.sh

# 4. Access at http://localhost:8080
```

**Or simply double-click:** `Launch Asset Hub.command`

## 📊 System Architecture

### Data Source (READ-ONLY)
```
OneDrive-VitalPlanet/Vital Planet Art/Packaging/VP PACKAGING/
├── Human/
│   ├── Current/           # 70 active products, 8,000+ assets
│   └── Work in Progress/  # Development projects  
└── Pet/
    ├── Current/           # 36 active products, 2,300+ assets
    └── Work in Progress/  # Pet development projects
```

### Technical Stack
```
Cloud Dashboard/
├── backend/
│   ├── scanner/           # Multi-directory asset scanning
│   │   ├── asset_scanner.py      # Main scanner with multi-dir support
│   │   ├── file_analyzer.py      # VP-specific classification logic
│   │   └── data_models.py        # Enhanced data structures
│   ├── config/            # Environment & settings management
│   └── api/               # Flask server with multi-dir endpoints
├── dashboard.js           # Enhanced UI with navigation toggles
├── enhancements.css       # Multi-tier navigation styling
└── assets_index.json     # Comprehensive 106-product database
```

## 🎯 Business Logic Understanding

### Product Organization (As-Is in OneDrive)
- **19xxx Human Products**: Probiotics (FG/SS), IntenseCare, Digestive Health
- **13xxx-18xxx Pet Products**: Dog/Cat/Horse/Bird formulations
- **Naming Convention**: ProductCode-Type (B=Box, L=Label, P=Pouch) + Version
- **Asset Structure**: Main files + Links/ + OLD VERSIONS/ + PRINT READY/

### Asset Classification Intelligence
```
Box Art (5,600 assets)    → B-designated files, retail packaging
Label Art (4,312 assets)  → L-designated files, bottle labels  
Print Ready (405 assets)  → PDF/ZIP files in production folders
3D Mockups               → PNG files in mockup directories
Archive Assets           → Files in OLD VERSIONS/, Archive/ folders
```

## 📈 Dashboard Capabilities

### Multi-Tier Navigation
- **Product Line Filter**: Human / Pet / Both
- **Status Filter**: Current / Work in Progress / All  
- **File Type Filter**: PNG / AI / PSD / PDF / Other
- **Search**: Product codes, names, categories

### Asset Management
- **Preview Images**: Direct image viewing for PNGs/JPGs
- **Download Assets**: One-click file access
- **Path Management**: Copy file paths, open in Finder
- **Status Indicators**: Visual product line and status badges

## 🔧 Configuration

### Environment Setup (.env)
```bash
VP_ASSET_SOURCE_PATH=/Users/[user]/Library/CloudStorage/OneDrive-VitalPlanet
VP_ENV=production
LOG_LEVEL=INFO
```

### Customization Options
- **Scan Directories**: Configure which folders to include
- **Asset Classifications**: Modify recognition patterns
- **UI Themes**: Adjust brand colors and styling

## 📊 Performance & Scale

- **Scan Speed**: ~1 second for 106 products, 10,300+ assets
- **Memory Efficient**: Concurrent processing with thread pools
- **Scalable**: Handles growing asset libraries automatically
- **Reliable**: Comprehensive error handling and logging

## 🎨 Brand Integration

### Vital Planet Colors
- **Primary**: #732d83 (Brand Purple)
- **Human Products**: Purple gradient badges
- **Pet Products**: Green gradient badges  
- **Typography**: Professional, clean interface

---

## 🛠️ Development Notes

### Single Cohesive Implementation
- ✅ **Consolidated Setup**: One `setup.sh` script handles all dependencies
- ✅ **Multi-Directory Scanner**: Unified scanning across all product lines
- ✅ **Enhanced Web Server**: Updated to use multi-directory data by default
- ✅ **No Confusion**: Removed duplicate scripts and setup processes

### OneDrive Integration Philosophy
- **Read-Only Access**: Never modifies your OneDrive structure
- **Preserves Organization**: Respects existing file hierarchy  
- **Business Logic Aware**: Understands VP naming conventions
- **Asset Intelligence**: Knows Current vs Archive vs Print Ready

*Professional asset management designed specifically for Vital Planet's workflow*