# Vital Planet Asset Hub - Business Requirements

## Executive Summary

The Vital Planet Asset Hub addresses critical workflow inefficiencies in the company's packaging design asset management. With over 69 products and 7,900+ design assets stored in deeply nested folder structures, the design and marketing teams spend significant time navigating to find specific files. This tool provides immediate visual access to all assets while preserving the existing organizational structure.

## Business Problem

### Current Challenges
- **Time Waste**: 5-10 minutes per asset lookup due to deep folder navigation
- **Asset Discovery**: Difficult to see what 3D mockups exist for products
- **Version Control**: Hard to distinguish current vs. archived versions
- **Team Efficiency**: New team members struggle with folder organization
- **Print Production**: Locating print-ready files requires multiple folder traversals

### Cost Impact
- Estimated 2-3 hours weekly per design team member in navigation time
- Delayed project timelines due to asset location overhead
- Increased onboarding time for new team members

## Solution Overview

The Vital Planet Asset Hub provides a web-based dashboard that:
1. **Indexes** all packaging assets without moving files
2. **Categorizes** products by type (VF FG, VF SS, IntenseCare, etc.)
3. **Visualizes** asset availability with preview capabilities  
4. **Searches** across all products and asset types
5. **Links** directly to files in their original locations

## Functional Requirements

### FR-001: Asset Indexing
- System SHALL scan the OneDrive packaging folder automatically
- System SHALL classify assets by type (3D Mockup, Box Art, Label Art, Print Ready, Archive)
- System SHALL identify product codes and categories
- System SHALL track file metadata (size, modification date, path)
- System SHALL complete full scan within 5 minutes

### FR-002: Product Categorization
- System SHALL categorize products into:
  - Vital Flora FG (Freeze-Dried)
  - Vital Flora SS (Shelf-Stable) 
  - IntenseCare FG/SS
  - Digestive Health
  - Organic Flora
  - Amazon Kits
  - Other
- System SHALL display asset counts per category

### FR-003: Search and Filtering
- System SHALL support text search by product code and name
- System SHALL filter by product category
- System SHALL filter by asset type
- System SHALL provide real-time search results
- System SHALL support keyboard shortcuts (/ for search, ESC to close modals)

### FR-004: Asset Visualization
- System SHALL display product cards with key asset counts
- System SHALL show 3D mockup, box art, label art, and print-ready file counts
- System SHALL open detailed asset views in modal dialogs
- System SHALL organize assets by current vs. archive status

### FR-005: File Access
- System SHALL provide direct links to original file locations
- System SHALL support "Open in Finder" functionality
- System SHALL copy file paths to clipboard
- System SHALL maintain all file paths as read-only references

### FR-006: Data Management
- System SHALL save asset index as JSON for portability
- System SHALL support manual and automatic index refreshing
- System SHALL handle missing or moved files gracefully
- System SHALL preserve index history for recovery

## Technical Requirements

### TR-001: Performance
- Web interface SHALL load within 3 seconds
- Search results SHALL appear within 1 second
- Asset scanning SHALL not exceed 10 minutes for full catalog

### TR-002: Compatibility
- System SHALL run on macOS (primary)
- System SHALL support modern web browsers (Chrome, Safari, Firefox)
- System SHALL work with OneDrive file paths
- System SHALL handle spaces and special characters in file names

### TR-003: Reliability
- System SHALL handle file system errors without crashing
- System SHALL provide error logging and recovery
- System SHALL maintain data integrity during scans

### TR-004: Usability
- Interface SHALL follow Vital Planet visual branding (#732d83 primary color)
- System SHALL be intuitive for non-technical users
- System SHALL provide contextual help and documentation

## Security Requirements

### SR-001: Data Access
- System SHALL NOT modify or move any source files
- System SHALL only read file metadata and paths
- System SHALL store index data locally only

### SR-002: Network Security
- Dashboard SHALL run locally only (no external network access required)
- No sensitive data SHALL be transmitted outside the local system

## Operational Requirements

### OR-001: Deployment
- System SHALL install with single script execution
- System SHALL require minimal configuration (OneDrive path only)
- System SHALL include automated setup documentation

### OR-002: Maintenance
- System SHALL support automated asset re-scanning
- System SHALL provide usage analytics and error reporting
- System SHALL include backup and recovery procedures

### OR-003: Training
- System SHALL include user manual and quick start guide
- System SHALL provide team training materials
- System SHALL document common workflows and troubleshooting

## Success Metrics

### Primary KPIs
- **Time Reduction**: 80% decrease in asset location time
- **User Adoption**: 90% of design team using within 30 days
- **Asset Coverage**: 100% of packaging assets indexed and accessible

### Secondary Metrics
- **Search Accuracy**: 95% successful asset location on first search
- **System Uptime**: 99% availability during business hours  
- **User Satisfaction**: 4.5/5 rating in team feedback

## Implementation Phases

### Phase 1: Core Functionality (Week 1)
- Asset scanning engine
- Basic web dashboard
- Product categorization
- Search and filtering

### Phase 2: Enhanced Features (Week 2)
- Asset preview capabilities
- Advanced filtering options
- Performance optimization
- Error handling

### Phase 3: Production Deployment (Week 3)
- Documentation completion
- Team training
- Production deployment
- Monitoring setup

## Risk Assessment

### Technical Risks
- **OneDrive Path Changes**: Mitigated by configurable path settings
- **Large File Volumes**: Managed through efficient scanning algorithms
- **Cross-Platform Issues**: Addressed with comprehensive testing

### Business Risks
- **User Resistance**: Mitigated through training and gradual rollout
- **File System Changes**: Handled through flexible scanning logic
- **Integration Complexity**: Minimized by read-only, non-invasive approach

## Conclusion

The Vital Planet Asset Hub represents a strategic investment in team productivity and workflow optimization. By providing instant access to the company's extensive design asset library, it eliminates a major friction point in the creative process while preserving all existing organizational structures and workflows.