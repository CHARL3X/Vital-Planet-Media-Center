# Vital Planet Asset Hub - User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Searching and Filtering](#searching-and-filtering)
4. [Viewing Product Assets](#viewing-product-assets)
5. [Asset Management](#asset-management)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Features](#advanced-features)

## Getting Started

### First Time Setup
1. **Install the Asset Hub**
   ```bash
   cd /Users/MKTG018/Desktop/Cloud Dashboard
   ./scripts/setup.sh
   ```

2. **Configure Your OneDrive Path**
   - Edit the `.env` file
   - Update `VP_ASSET_SOURCE_PATH` with your OneDrive location
   - Default path is usually correct for Vital Planet team members

3. **Build Your Asset Index**
   ```bash
   ./scripts/scan_assets.sh
   ```
   This process takes 3-5 minutes and indexes all your packaging assets.

4. **Launch the Dashboard**
   ```bash
   ./scripts/start_server.sh
   ```
   The dashboard will open automatically in your browser at `http://localhost:8080`

### Quick Launch (After Setup)
Simply double-click the **"Launch Asset Hub.command"** file on your desktop.

---

## Dashboard Overview

### Header Section
- **🌱 VP Packaging Dashboard**: Main title with Vital Planet branding
- **Statistics**: Live counts of total products and assets indexed
- **Primary Color**: Custom Vital Planet purple (#732d83)

### Main Interface
The dashboard displays your packaging assets in an organized grid format:

#### Product Cards
Each product is displayed as a card containing:
- **Product Code**: 5-digit identifier (e.g., 19207)
- **Product Name**: Full product description
- **Category Badge**: Product line classification
- **Asset Summary**: Quick counts of key asset types
  - 3D Mockups
  - Box Art
  - Label Art  
  - Print Ready Files

#### Category Classifications
Products are automatically categorized into:
- **Vital Flora FG**: Freeze-dried probiotic products
- **Vital Flora SS**: Shelf-stable probiotic products  
- **IntenseCare FG/SS**: Targeted probiotic solutions
- **Digestive Health**: Broader digestive wellness products
- **Organic Flora**: Organic probiotic formulations
- **Amazon Kits**: Special bundled products
- **Other**: Miscellaneous or uncategorized items

---

## Searching and Filtering

### Search Functionality
- **Text Search**: Type in the search bar to find products by code or name
- **Keyboard Shortcut**: Press `/` to quickly focus the search field
- **Real-time Results**: Results update as you type
- **Clear Search**: Click "Clear" button to reset

#### Search Examples:
- `19207` - Find product by exact code
- `LiverPURE` - Search by product name
- `Omega` - Find all omega products
- `IntenseCare` - Find all IntenseCare products

### Filter Options

#### Category Filter
Select from dropdown to show only products in specific categories:
- All Categories (default)
- Vital Flora FG
- Vital Flora SS
- IntenseCare FG
- IntenseCare SS
- Digestive Health
- Organic Flora
- Amazon Kits
- Other

#### Asset Type Filter
Filter products by the types of assets they contain:
- All Types (default)
- 3D Mockups
- Box Art
- Label Art
- Print Ready
- Archive
- Templates
- Other

### Refresh Data
Click the **"Refresh Data"** button to re-scan your assets and update the index with any new or changed files.

---

## Viewing Product Assets

### Opening Product Details
Click any product card to open the detailed asset view in a modal dialog.

### Asset Organization Tabs
The asset detail view has three tabs:

#### Current Tab
- Shows only current/active versions of assets
- Excludes old drafts and archived files
- Best for finding the latest versions

#### Archive Tab  
- Shows historical versions and drafts
- Useful for version comparison or recovery
- Includes files in "Old," "Draft," and "Archive" folders

#### All Assets Tab
- Complete view of every file in the product folder
- Comprehensive listing for thorough review

### Asset Information
Each asset displays:
- **File Name**: Original filename
- **Asset Type**: Automatically classified (3D Mockup, Box Art, etc.)
- **File Size**: Human-readable file size
- **Last Modified**: When the file was last changed
- **Relative Path**: Location within the product folder

---

## Asset Management

### Opening Files
Each asset has action buttons:

#### Open Button
- **Design Files** (.ai, .psd): Opens in default application
- **Images** (.png, .jpg): Opens in image viewer
- **PDFs**: Opens in PDF reader
- **Other Files**: Attempts to open with system default

#### Copy Path Button
- Copies the full file path to your clipboard
- Useful for:
  - Email communication
  - File sharing
  - Script automation
  - Documentation

### Folder Access
- **"Open Folder"** button on each product card
- Opens the product's main folder in Finder
- Provides direct access to the file system

### File Path Display
When files can't be opened directly:
- Path is displayed in a modal dialog
- Full path can be copied to clipboard
- Manual navigation instructions provided

---

## Troubleshooting

### Common Issues

#### "Asset index not found" Error
**Solution**: Run the asset scanner
```bash
./scripts/scan_assets.sh
```

#### Dashboard Won't Load
**Possible Causes**:
1. **Port already in use**: Try stopping other servers
   ```bash
   ./scripts/stop_server.sh
   ```
2. **Permission issues**: Ensure scripts are executable
   ```bash
   chmod +x scripts/*.sh
   ```

#### No Products Showing
**Check**:
1. OneDrive path is correct in `.env` file
2. OneDrive is synced and accessible
3. Product folders follow naming convention (5-digit codes)

#### Search Not Working
1. Refresh the page
2. Check browser console for JavaScript errors
3. Try restarting the dashboard

#### Files Won't Open
**macOS Security**:
- Some files may require security approval
- Go to System Preferences > Security & Privacy
- Allow the blocked application

### Performance Issues

#### Slow Loading
- **Large Asset Libraries**: Normal for 7,000+ assets
- **Network Issues**: Ensure OneDrive is fully synced
- **Memory**: Close other applications if needed

#### Scan Taking Too Long
- **Normal Duration**: 3-10 minutes for full scan
- **Optimization**: Close other OneDrive applications
- **Interruption**: Use Ctrl+C to cancel if needed

### Getting Help

#### Log Files
Check these locations for detailed error information:
- `logs/vital_planet_asset_hub.log`
- `logs/scan_YYYYMMDD_HHMMSS.log`

#### Reset Installation
If major issues occur:
```bash
# Backup your .env settings first
cp .env .env.backup
# Remove and reinstall
rm -rf venv
./scripts/setup.sh
cp .env.backup .env
```

---

## Advanced Features

### Keyboard Shortcuts
- **`/`**: Focus search field
- **`Escape`**: Close modal dialogs
- **`Ctrl+C`**: Stop server (in terminal)

### Automated Scanning
Set up automatic daily scans:
```bash
# Add to crontab (runs daily at 6 AM)
0 6 * * * cd /path/to/Cloud\ Dashboard && ./scripts/scan_assets.sh
```

### Custom Configuration
Edit `.env` file for advanced settings:
- `VP_HOST`: Change server host (default: localhost)
- `VP_PORT`: Change port (default: 8080)  
- `VP_LOG_LEVEL`: Adjust logging verbosity
- `VP_SCAN_TIMEOUT`: Modify scan timeout

### API Access
The dashboard provides API endpoints for integration:
- `GET /api/stats` - Dashboard statistics
- `GET /api/health` - System health check
- `POST /api/scan` - Trigger new scan

### Backup and Recovery
Asset indices are automatically backed up:
- Location: `backups/` folder
- Format: `assets_index_YYYYMMDD_HHMMSS.json`
- Retention: Configurable in settings

---

## Best Practices

### Daily Workflow
1. **Morning**: Check for new assets by clicking "Refresh Data"
2. **Project Work**: Use search and filters to find assets quickly
3. **File Sharing**: Use "Copy Path" for email communication
4. **End of Day**: Dashboard runs automatically, no action needed

### File Organization Tips
- Keep the existing folder structure intact
- Use consistent naming in new files
- Place new mockups in appropriate "3D" or "Mock Up" folders
- Mark drafts clearly in file names

### Team Collaboration
- Share product codes rather than file paths
- Use category filters to focus team discussions
- Bookmark frequently accessed products
- Document asset locations in project files

---

## Support

### Internal Support
- **Marketing Technology Team**: Technical issues
- **Design Team Lead**: Workflow questions  
- **IT Support**: Infrastructure and permissions

### Self-Service
- Check log files for error details
- Review this manual for common solutions
- Use built-in refresh and reset features
- Consult the troubleshooting section

### Feature Requests
Submit enhancement ideas to the Marketing Technology team:
- New asset type classifications
- Additional search capabilities
- Integration with other tools
- Workflow optimizations

---

*Vital Planet Asset Hub v1.0 - Internal Use Only*