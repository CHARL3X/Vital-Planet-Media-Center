# Vital Planet Asset Hub - Deployment Guide

## Overview

This deployment guide covers installation, configuration, and maintenance of the Vital Planet Asset Hub in production environments.

## System Requirements

### Minimum Requirements
- **Operating System**: macOS 10.15+ (Catalina), Windows 10, or Linux
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100MB for application, 500MB for asset indices
- **Network**: OneDrive access for asset scanning

### Recommended Environment
- **macOS**: 12.0+ (Monterey) for optimal compatibility
- **Python**: 3.11+ for best performance
- **Memory**: 16GB RAM for large asset libraries
- **Storage**: SSD for faster scanning performance

## Pre-Installation Checklist

### OneDrive Configuration
- [ ] OneDrive is installed and syncing
- [ ] Vital Planet OneDrive account is connected
- [ ] Packaging folder is fully synchronized
- [ ] User has read access to all packaging directories

### System Permissions
- [ ] User has admin rights (for initial setup only)
- [ ] Python installation permissions
- [ ] Network access for package downloads
- [ ] File system access to OneDrive folders

## Installation Methods

### Method 1: Automated Setup (Recommended)

1. **Download and Extract**
   ```bash
   # Download the Asset Hub package
   cd /Users/$(whoami)/Desktop
   # Extract to "Cloud Dashboard" folder
   ```

2. **Run Setup Script**
   ```bash
   cd "Cloud Dashboard"
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configure Environment**
   ```bash
   # Edit .env file with your settings
   nano .env
   ```

4. **Initial Asset Scan**
   ```bash
   ./scripts/scan_assets.sh
   ```

5. **Launch Dashboard**
   ```bash
   ./scripts/start_server.sh
   ```

### Method 2: Manual Installation

1. **Create Project Directory**
   ```bash
   mkdir -p "/Users/$(whoami)/Desktop/Cloud Dashboard"
   cd "/Users/$(whoami)/Desktop/Cloud Dashboard"
   ```

2. **Set Up Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OneDrive path
   ```

4. **Create Directory Structure**
   ```bash
   mkdir -p data logs backups temp
   ```

5. **Run Initial Scan**
   ```bash
   python3 backend/scanner/asset_scanner.py
   ```

## Configuration

### Environment Variables (.env)

```bash
# Required Settings
VP_ASSET_SOURCE_PATH="/Users/MKTG018/Library/CloudStorage/OneDrive-VitalPlanet/Vital Planet Art/Packaging/VP PACKAGING/Human/Current"
VP_ENV=production

# Optional Settings
VP_HOST=localhost
VP_PORT=8080
VP_LOG_LEVEL=INFO
VP_DEBUG=false
```

### Path Configuration

#### Standard OneDrive Paths
```bash
# Personal OneDrive
/Users/$(whoami)/OneDrive - VitalPlanet/...

# Business OneDrive (most common)
/Users/$(whoami)/Library/CloudStorage/OneDrive-VitalPlanet/...
```

#### Custom Path Detection
```bash
# Auto-detect OneDrive path
find /Users/$(whoami) -name "*OneDrive*" -type d 2>/dev/null | head -5
```

### Performance Tuning

#### Large Asset Libraries (5000+ files)
```bash
VP_CONCURRENT_THREADS=2
VP_SCAN_TIMEOUT=1200
VP_MAX_SCAN_DEPTH=8
```

#### Memory-Constrained Systems
```bash
VP_CONCURRENT_THREADS=1
VP_CACHE_ENABLED=false
```

## Production Deployment

### Single User Deployment

1. **Desktop Installation**
   - Install in user's desktop for personal use
   - Use default settings for simplicity
   - Create desktop shortcuts for easy access

2. **Login Item (Auto-start)**
   ```bash
   # macOS: Add to Login Items
   osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Users/$(whoami)/Desktop/Cloud Dashboard/Launch Asset Hub.command", hidden:false}'
   ```

### Team Deployment

1. **Shared Network Location**
   ```bash
   # Install on shared drive accessible to design team
   /Volumes/SharedDrive/Tools/VitalPlanetAssetHub/
   ```

2. **Individual Configuration**
   - Each user maintains their own `.env` file
   - Shared OneDrive path, personal port assignments
   - Individual log files and temp directories

### Server Deployment (Advanced)

1. **Dedicated Server Setup**
   ```bash
   # Ubuntu/CentOS server environment
   sudo apt update
   sudo apt install python3 python3-venv nginx
   ```

2. **Process Management**
   ```bash
   # Using systemd (Linux)
   sudo cp scripts/vital-planet-hub.service /etc/systemd/system/
   sudo systemctl enable vital-planet-hub
   sudo systemctl start vital-planet-hub
   ```

3. **Reverse Proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name vital-assets.internal;
       
       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Security Configuration

### Network Security
```bash
# Restrict to localhost only (default)
VP_HOST=127.0.0.1
VP_ALLOWED_HOSTS=localhost,127.0.0.1

# Team access (same network)
VP_HOST=0.0.0.0
VP_ALLOWED_HOSTS=192.168.1.0/24
```

### File System Permissions
```bash
# Read-only access to asset directories
chmod -R 755 /path/to/assets/
# Application has full control of its own directories
chmod -R 755 /path/to/Cloud\ Dashboard/
```

### Log File Security
```bash
# Restrict log file access
chmod 600 logs/*.log
# Log rotation setup
logrotate -d scripts/vital-planet-hub.logrotate
```

## Monitoring and Maintenance

### Health Checks
```bash
# Automated health check
curl http://localhost:8080/api/health

# Manual service check
./scripts/status.sh
```

### Log Monitoring
```bash
# Real-time log viewing
tail -f logs/vital_planet_asset_hub.log

# Error pattern detection
grep "ERROR\|CRITICAL" logs/*.log
```

### Performance Monitoring
```bash
# Resource usage
ps aux | grep python3
du -sh data/ logs/ backups/

# Asset count tracking
curl -s http://localhost:8080/api/stats | jq '.total_assets'
```

### Automated Maintenance

#### Daily Asset Refresh
```bash
# Crontab entry
0 6 * * * cd /path/to/Cloud\ Dashboard && ./scripts/scan_assets.sh >> logs/cron.log 2>&1
```

#### Weekly Cleanup
```bash
# Remove old backups (keep 4 weeks)
find backups/ -name "assets_index_*.json" -mtime +28 -delete

# Rotate logs
logrotate scripts/vital-planet-hub.logrotate
```

#### Monthly Reports
```bash
# Generate usage statistics
python3 scripts/generate_report.py > reports/monthly_$(date +%Y%m).txt
```

## Backup and Recovery

### Asset Index Backup
- **Automatic**: Created on each scan
- **Location**: `backups/assets_index_TIMESTAMP.json`
- **Retention**: 30 days (configurable)

### Configuration Backup
```bash
# Backup critical configuration
cp .env config_backup_$(date +%Y%m%d).env
tar -czf vital_planet_hub_backup.tar.gz .env logs/ data/
```

### Recovery Procedures

#### Index Corruption
```bash
# Restore from backup
cp backups/assets_index_YYYYMMDD_HHMMSS.json assets_index.json
./scripts/start_server.sh
```

#### Complete System Recovery
```bash
# Clean installation
rm -rf venv data logs
./scripts/setup.sh
# Restore configuration
cp config_backup.env .env
./scripts/scan_assets.sh
```

## Troubleshooting

### Common Deployment Issues

#### Permission Errors
```bash
# Fix script permissions
chmod +x scripts/*.sh
# Fix Python module access
chown -R $(whoami) venv/
```

#### OneDrive Path Issues
```bash
# Verify OneDrive sync
ls -la "/Users/$(whoami)/Library/CloudStorage/"
# Test access to packaging folder
ls "/path/to/OneDrive/Vital Planet Art/Packaging/"
```

#### Port Conflicts
```bash
# Find conflicting processes
lsof -i :8080
# Change port in .env
VP_PORT=8081
```

#### Memory Issues
```bash
# Monitor memory usage during scan
while true; do ps -o pid,vsz,rss,pcpu,comm -p $(pgrep -f asset_scanner); sleep 5; done
```

### Performance Troubleshooting

#### Slow Scanning
- Reduce concurrent threads
- Exclude unnecessary file types
- Check OneDrive sync status
- Verify disk space availability

#### Web Interface Lag
- Clear browser cache
- Restart dashboard server
- Check network connectivity
- Verify JSON index integrity

## Scaling and Optimization

### Large Team Deployment
```bash
# Multiple instance deployment
VP_PORT=8080  # Designer 1
VP_PORT=8081  # Designer 2
VP_PORT=8082  # Marketing Team
```

### Load Balancing (Advanced)
```bash
# HAProxy configuration for multiple instances
backend vital_planet_hub
    balance roundrobin
    server hub1 127.0.0.1:8080 check
    server hub2 127.0.0.1:8081 check
```

### Caching Optimization
```bash
# Enable asset caching
VP_CACHE_ENABLED=true
VP_CACHE_DURATION=7200

# Disk caching for large indices
VP_DISK_CACHE_ENABLED=true
VP_DISK_CACHE_PATH="./cache"
```

## Upgrade Procedures

### Version Updates
1. **Backup Current Installation**
   ```bash
   tar -czf vital_planet_hub_v1.0_backup.tar.gz .
   ```

2. **Download New Version**
   ```bash
   # Extract new version to temporary location
   # Compare configuration changes
   ```

3. **Migrate Configuration**
   ```bash
   # Copy .env and any customizations
   # Update dependency requirements
   pip install -r requirements.txt --upgrade
   ```

4. **Test New Version**
   ```bash
   # Run in test mode
   VP_ENV=testing ./scripts/start_server.sh
   ```

5. **Deploy to Production**
   ```bash
   # Stop current version
   ./scripts/stop_server.sh
   # Start new version
   ./scripts/start_server.sh
   ```

---

## Support and Documentation

### Internal Resources
- **Technical Documentation**: `/docs/` directory
- **API Reference**: `/docs/API_REFERENCE.md`
- **User Manual**: `/docs/USER_MANUAL.md`

### External Dependencies
- **Python Packages**: Listed in `requirements.txt`
- **System Dependencies**: Documented in setup scripts
- **OneDrive Integration**: Microsoft OneDrive sync client

### Contact Information
- **Development Team**: Marketing Technology
- **System Administration**: IT Support
- **Business Requirements**: Design Team Lead

---

*Vital Planet Asset Hub v1.0 - Deployment Guide*