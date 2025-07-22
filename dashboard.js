/**
 * Vital Planet Packaging Dashboard
 * JavaScript for the web interface
 */

class PackagingDashboard {
    constructor() {
        this.data = null;
        this.filteredProducts = [];
        this.currentProduct = null;
        
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadData();
        this.updateStats();
        this.renderProducts();
    }

    bindEvents() {
        // Search functionality
        document.getElementById('searchInput').addEventListener('input', () => {
            this.filterProducts();
        });

        document.getElementById('clearSearch').addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            this.filterProducts();
        });

        // Filter dropdowns
        document.getElementById('categoryFilter').addEventListener('change', () => {
            this.filterProducts();
        });

        document.getElementById('assetTypeFilter').addEventListener('change', () => {
            this.filterProducts();
        });

        document.getElementById('fileTypeFilter').addEventListener('change', () => {
            this.filterProducts();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });

        // Modal controls
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeModal();
        });

        // Click outside modal to close
        document.getElementById('assetModal').addEventListener('click', (e) => {
            if (e.target.id === 'assetModal') {
                this.closeModal();
            }
        });

        // Tab switching in modal
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Navigation toggle handlers
        document.getElementById('productLineToggle').addEventListener('click', (e) => {
            if (e.target.classList.contains('toggle-btn')) {
                // Update active state
                document.querySelectorAll('#productLineToggle .toggle-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Filter products
                this.filterProducts();
            }
        });

        document.getElementById('statusToggle').addEventListener('click', (e) => {
            if (e.target.classList.contains('toggle-btn')) {
                // Update active state
                document.querySelectorAll('#statusToggle .toggle-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Filter products
                this.filterProducts();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
            if (e.key === '/' && !e.target.matches('input, textarea')) {
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }
        });
    }

    async loadData() {
        try {
            document.getElementById('loading').style.display = 'block';
            
            const response = await fetch('assets_index.json');
            if (!response.ok) throw new Error('Failed to load asset data');
            
            this.data = await response.json();
            this.filteredProducts = Object.values(this.data.products);
            
            document.getElementById('loading').style.display = 'none';
        } catch (error) {
            console.error('Error loading data:', error);
            document.getElementById('loading').innerHTML = `
                <div class="error">
                    <p>Error loading packaging data. Please make sure assets_index.json exists and is accessible.</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.textContent = 'Refreshing...';
        refreshBtn.disabled = true;

        try {
            // Re-run the scanner
            const response = await fetch('/refresh-assets', { method: 'POST' });
            if (response.ok) {
                await this.loadData();
                this.updateStats();
                this.renderProducts();
            }
        } catch (error) {
            console.warn('Auto-refresh failed, reloading page...');
            location.reload();
        }

        refreshBtn.textContent = 'Refresh Data';
        refreshBtn.disabled = false;
    }

    updateStats() {
        if (!this.data) return;

        const totalProducts = this.data.metadata.total_products;
        const totalAssets = this.data.metadata.total_assets;

        document.getElementById('totalProducts').textContent = `${totalProducts} Products`;
        document.getElementById('totalAssets').textContent = `${totalAssets.toLocaleString()} Assets`;
    }

    filterProducts() {
        if (!this.data) return;

        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const categoryFilter = document.getElementById('categoryFilter').value;
        const assetTypeFilter = document.getElementById('assetTypeFilter').value;
        const fileTypeFilter = document.getElementById('fileTypeFilter').value;
        
        // Get navigation filter states
        const productLineFilter = document.querySelector('#productLineToggle .toggle-btn.active')?.dataset?.line || 'human';
        const statusFilter = document.querySelector('#statusToggle .toggle-btn.active')?.dataset?.status || 'current';

        this.filteredProducts = Object.values(this.data.products).filter(product => {
            // Search filter
            const matchesSearch = !searchTerm || 
                product.code.toLowerCase().includes(searchTerm) ||
                product.name.toLowerCase().includes(searchTerm);

            // Category filter
            const matchesCategory = categoryFilter === 'all' || product.category === categoryFilter;

            // Product Line filter
            const productLine = (product.product_line || 'Human').toLowerCase();
            const matchesProductLine = productLineFilter === 'both' || 
                (productLineFilter === 'human' && productLine === 'human') ||
                (productLineFilter === 'pet' && productLine === 'pet');

            // Status filter  
            const productStatus = (product.status || 'Current').toLowerCase();
            const matchesStatus = statusFilter === 'all' ||
                (statusFilter === 'current' && productStatus === 'current') ||
                (statusFilter === 'wip' && productStatus.includes('progress'));

            // Asset type filter (if a specific asset type is selected)
            const matchesAssetType = assetTypeFilter === 'all' || 
                product.assets.some(asset => asset.type === assetTypeFilter);

            // File type filter
            const matchesFileType = fileTypeFilter === 'all' || 
                product.assets.some(asset => {
                    const ext = asset.extension.replace('.', '').toLowerCase();
                    if (fileTypeFilter === 'other') {
                        return !['png', 'jpg', 'jpeg', 'ai', 'psd', 'pdf'].includes(ext);
                    }
                    return ext === fileTypeFilter;
                });

            return matchesSearch && matchesCategory && matchesProductLine && 
                   matchesStatus && matchesAssetType && matchesFileType;
        });

        this.renderProducts();
    }

    renderProducts() {
        const grid = document.getElementById('productsGrid');
        
        if (this.filteredProducts.length === 0) {
            grid.innerHTML = `
                <div class="no-results">
                    <h3>No products found</h3>
                    <p>Try adjusting your search or filters</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.filteredProducts.map(product => this.createProductCard(product)).join('');
    }

    createProductCard(product) {
        const assetCounts = this.getAssetCounts(product.assets);
        const mockupCount = assetCounts['3D Mockup'] || 0;
        const boxCount = assetCounts['Box Art'] || 0;
        const labelCount = assetCounts['Label Art'] || 0;
        const printCount = assetCounts['Print Ready'] || 0;

        const productLine = (product.product_line || 'Human').toLowerCase();
        const status = (product.status || 'Current').toLowerCase();
        const statusClass = status.includes('progress') ? 'wip' : 'current';

        return `
            <div class="product-card" 
                 data-line="${productLine}" 
                 data-status="${statusClass}"
                 onclick="dashboard.openProductModal('${product.code}')">
                <div class="product-line-badge ${productLine}">${product.product_line || 'Human'}</div>
                <div class="product-header">
                    <div class="product-code">${product.code}</div>
                    <div class="product-name">${this.truncateText(product.name, 60)}</div>
                    <span class="product-category">${product.category}</span>
                </div>
                <div class="product-body">
                    <div class="asset-summary">
                        <div class="asset-count">
                            <span class="asset-count-number">${mockupCount}</span>
                            <span class="asset-count-label">3D Mockups</span>
                        </div>
                        <div class="asset-count">
                            <span class="asset-count-number">${boxCount}</span>
                            <span class="asset-count-label">Box Art</span>
                        </div>
                        <div class="asset-count">
                            <span class="asset-count-number">${labelCount}</span>
                            <span class="asset-count-label">Label Art</span>
                        </div>
                        <div class="asset-count">
                            <span class="asset-count-number">${printCount}</span>
                            <span class="asset-count-label">Print Ready</span>
                        </div>
                    </div>
                    <div class="product-actions" onclick="event.stopPropagation()">
                        <button class="btn btn-primary" onclick="dashboard.openProductModal('${product.code}')">
                            View Assets
                        </button>
                        <button class="btn" onclick="dashboard.openInFinder('${product.folder_path}')">
                            Open Folder
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getAssetCounts(assets) {
        const counts = {};
        assets.forEach(asset => {
            counts[asset.type] = (counts[asset.type] || 0) + 1;
        });
        return counts;
    }

    openProductModal(productCode) {
        this.currentProduct = this.data.products[productCode];
        if (!this.currentProduct) return;

        document.getElementById('modalTitle').textContent = 
            `${this.currentProduct.code} - ${this.currentProduct.name}`;

        // Set default tab to current
        this.switchTab('current');
        
        document.getElementById('assetModal').style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        document.getElementById('assetModal').style.display = 'none';
        document.body.style.overflow = 'auto';
        this.currentProduct = null;
    }

    switchTab(tabType) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabType}"]`).classList.add('active');

        // Filter assets based on tab
        let assetsToShow = this.currentProduct.assets;
        
        switch(tabType) {
            case 'current':
                assetsToShow = assetsToShow.filter(asset => asset.is_current);
                break;
            case 'archive':
                assetsToShow = assetsToShow.filter(asset => !asset.is_current);
                break;
            case 'all':
                // Show all assets
                break;
        }

        this.renderAssetsList(assetsToShow);
    }

    renderAssetsList(assets) {
        const container = document.getElementById('assetsList');
        
        if (assets.length === 0) {
            container.innerHTML = '<p class="text-center">No assets found for this filter.</p>';
            return;
        }

        // Combine regular assets with grouped assets
        const allAssets = [...assets];
        
        // Add grouped assets from product (if any)
        if (this.currentProduct && this.currentProduct._grouped_assets) {
            allAssets.push(...this.currentProduct._grouped_assets);
        }

        // Group assets by type, but handle grouped assets properly
        const groupedAssets = {};
        allAssets.forEach(asset => {
            // For grouped assets, use the asset_type or type field
            const assetType = asset.asset_type || asset.type || 'Unknown';
            if (!groupedAssets[assetType]) {
                groupedAssets[assetType] = [];
            }
            groupedAssets[assetType].push(asset);
        });

        const html = Object.entries(groupedAssets)
            .sort(([a], [b]) => {
                // Prioritize 3D Mockup at the top
                if (a === '3D Mockup' && b !== '3D Mockup') return -1;
                if (b === '3D Mockup' && a !== '3D Mockup') return 1;
                return a.localeCompare(b);
            })
            .map(([type, typeAssets]) => {
                // Sort grouped assets first within each type
                const sortedAssets = typeAssets.sort((a, b) => {
                    if (a.is_grouped && !b.is_grouped) return -1;
                    if (!a.is_grouped && b.is_grouped) return 1;
                    return 0;
                });
                
                // Count individual assets vs grouped assets
                const groupedCount = typeAssets.filter(a => a.is_grouped).length;
                const individualCount = typeAssets.length - groupedCount;
                const totalItems = typeAssets.length;
                
                // Show meaningful count in header
                const countDisplay = groupedCount > 0 ? 
                    `${totalItems} items (${groupedCount} grouped)` : 
                    `${totalItems}`;
                    
                return `
                    <div class="asset-type-group">
                        <h3 class="asset-type-header">${type} (${countDisplay})</h3>
                        ${sortedAssets.map(asset => this.createAssetItem(asset)).join('')}
                    </div>
                `;
            }).join('');

        container.innerHTML = html;
    }

    createAssetItem(asset) {
        // Check if this is a grouped asset
        if (asset.is_grouped) {
            return this.createGroupedAssetItem(asset);
        }
        
        // Regular single asset item
        const fileSize = this.formatFileSize(asset.size);
        const modDate = asset.modified ? new Date(asset.modified).toLocaleDateString() : 'Unknown';
        const fileExt = asset.extension.replace('.', '').toLowerCase();
        const isImage = ['png', 'jpg', 'jpeg', 'gif'].includes(fileExt);
        
        
        // Create thumbnail if it's an image
        const thumbnailHtml = isImage ? 
            `<div class="asset-thumbnail">
                <img src="/api/thumbnail?path=${encodeURIComponent(asset.path)}&size=64" 
                     alt="${asset.name}" 
                     style="width: 64px; height: 64px; object-fit: cover; border-radius: 4px; cursor: pointer;"
                     onclick="dashboard.previewImage('${asset.path}', '${asset.name}')"
                     onerror="this.style.display='none'; this.parentElement.querySelector('.file-icon').style.display='inline';">
                <span class="file-icon" style="display: none;">${this.getFileIcon(fileExt)}</span>
            </div>` : 
            `<div class="asset-thumbnail">
                <span class="file-icon">${this.getFileIcon(fileExt)}</span>
            </div>`;
        
        return `
            <div class="asset-item" data-file-type="${fileExt}">
                ${thumbnailHtml}
                <div class="asset-info">
                    <div class="asset-name">
                        ${asset.name}
                    </div>
                    <div class="asset-meta">
                        <span class="asset-type">${asset.type}</span>
                        <span class="file-type-badge">${fileExt.toUpperCase()}</span>
                        <span>Size: ${fileSize}</span>
                        <span>Modified: ${modDate}</span>
                        <span>Path: ${asset.relative_path}</span>
                    </div>
                </div>
                <div class="asset-actions">
                    ${isImage ? `
                        <button class="btn btn-small btn-primary" onclick="dashboard.previewImage('${asset.path}', '${asset.name}')">
                            Preview
                        </button>
                    ` : ''}
                    <button class="btn btn-small" onclick="dashboard.downloadFile('${asset.path}', '${asset.name}')">
                        Download
                    </button>
                    <button class="btn btn-small" onclick="dashboard.openInFinder('${asset.path}')">
                        Open
                    </button>
                    <button class="btn btn-small" onclick="dashboard.copyPath('${asset.path}')">
                        Copy Path
                    </button>
                </div>
            </div>
        `;
    }

    createGroupedAssetItem(asset) {
        const fileSize = this.formatFileSize(asset.size);
        const modDate = asset.modified ? new Date(asset.modified).toLocaleDateString() : 'Unknown';
        const primaryExt = asset.extension.replace('.', '').toLowerCase();
        const isImage = ['png', 'jpg', 'jpeg', 'gif'].includes(primaryExt);
        
        // Create unique ID for this group
        const groupId = `group_${asset.base_name.replace(/[^a-zA-Z0-9]/g, '_')}`;
        
        // Create thumbnail for grouped asset using primary asset
        const thumbnailHtml = isImage ? 
            `<div class="asset-thumbnail">
                <img src="/api/thumbnail?path=${encodeURIComponent(asset.path)}&size=64" 
                     alt="${asset.base_name}" 
                     style="width: 64px; height: 64px; object-fit: cover; border-radius: 4px; cursor: pointer;"
                     onclick="dashboard.previewImage('${asset.path}', '${asset.name}')"
                     onerror="this.style.display='none'; this.parentElement.querySelector('.file-icon').style.display='inline';">
                <span class="file-icon" style="display: none;">${this.getFileIcon(primaryExt)}</span>
            </div>` : 
            `<div class="asset-thumbnail">
                <span class="file-icon">${this.getFileIcon(primaryExt)}</span>
            </div>`;
        
        return `
            <div class="asset-item grouped-asset" data-file-type="${primaryExt}">
                ${thumbnailHtml}
                <div class="asset-info">
                    <div class="asset-name">
                        ${asset.base_name}
                        <span class="group-badge">${asset.total_assets} formats</span>
                    </div>
                    <div class="asset-meta">
                        <span class="asset-type">${asset.type}</span>
                        <span class="format-badges">
                            ${asset.available_formats.map(format => 
                                `<span class="file-type-badge format-${format.toLowerCase()}">${format}</span>`
                            ).join('')}
                        </span>
                        <span>Total Size: ${fileSize}</span>
                        <span>Modified: ${modDate}</span>
                    </div>
                </div>
                <div class="asset-actions">
                    ${isImage ? `
                        <button class="btn btn-small btn-primary" onclick="dashboard.previewImage('${asset.path}', '${asset.name}')">
                            Preview
                        </button>
                    ` : ''}
                    <div class="dropdown">
                        <button class="btn btn-small dropdown-toggle" onclick="dashboard.toggleDownloadOptions('${groupId}')">
                            Download ▼
                        </button>
                        <div class="dropdown-menu" id="${groupId}">
                            ${asset.available_formats.map(format => {
                                const formatAsset = asset.related_assets.find(a => 
                                    a.extension.replace('.', '').toUpperCase() === format);
                                const formatType = format === 'PSD' ? 'Project File' : 
                                                 format === 'PNG' ? 'Image' : 'Image';
                                return formatAsset ? `
                                    <button class="dropdown-item" onclick="dashboard.downloadFile('${formatAsset.path}', '${formatAsset.name}')">
                                        ${format} (${formatType})
                                    </button>
                                ` : '';
                            }).join('')}
                        </div>
                    </div>
                    <button class="btn btn-small" onclick="dashboard.openInFinder('${asset.path}')">
                        Open
                    </button>
                    <button class="btn btn-small" onclick="dashboard.copyPath('${asset.path}')">
                        Copy Path
                    </button>
                </div>
            </div>
        `;
    }

    toggleDownloadOptions(groupId) {
        const dropdown = document.getElementById(groupId);
        const isVisible = dropdown.style.display === 'block';
        
        // Hide all other dropdowns first
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.display = 'none';
        });
        
        // Toggle this dropdown
        dropdown.style.display = isVisible ? 'none' : 'block';
        
        // Close dropdown when clicking outside
        if (!isVisible) {
            setTimeout(() => {
                const clickOutside = (e) => {
                    if (!dropdown.contains(e.target) && !e.target.classList.contains('dropdown-toggle')) {
                        dropdown.style.display = 'none';
                        document.removeEventListener('click', clickOutside);
                    }
                };
                document.addEventListener('click', clickOutside);
            }, 100);
        }
    }

    openInFinder(path) {
        // Try to open file via server endpoint
        console.log('Open file:', path);
        
        try {
            if (path.endsWith('.pdf') || path.endsWith('.png') || path.endsWith('.jpg') || path.endsWith('.jpeg')) {
                // Open images and PDFs in new tab
                const fileUrl = `/api/file?path=${encodeURIComponent(path)}`;
                window.open(fileUrl, '_blank');
            } else {
                // For other files, trigger download
                this.downloadFile(path, path.split('/').pop());
            }
        } catch (error) {
            console.error('Failed to open file:', error);
            this.showPathModal(path);
        }
    }
    
    revealInFinder(path) {
        // Show the file location to user
        console.log('Reveal in Finder:', path);
        this.showPathModal(path);
    }

    showPathModal(path) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h3>File Location</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div style="padding: 2rem;">
                    <p>File path:</p>
                    <code style="background: #f5f5f5; padding: 1rem; border-radius: 4px; display: block; margin: 1rem 0; word-break: break-all;">${path}</code>
                    <button class="btn btn-primary" onclick="dashboard.copyPath('${path}')">Copy Path</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    copyPath(path) {
        navigator.clipboard.writeText(path).then(() => {
            console.log('Path copied to clipboard:', path);
            this.showToast('Path copied to clipboard', 'success');
        }).catch(err => {
            console.error('Failed to copy path:', err);
            this.showToast('Failed to copy path', 'error');
        });
    }

    downloadFile(path, filename) {
        console.log('Download requested:', filename);
        
        try {
            // Use server endpoint to download file
            const downloadUrl = `/api/download?path=${encodeURIComponent(path)}`;
            
            // Create a temporary download link
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showToast(`Download initiated: ${filename}`, 'success');
        } catch (error) {
            console.error('Download failed:', error);
            this.showToast('Download failed. Please try again.', 'error');
        }
    }

    previewImage(path, filename) {
        console.log('Image preview requested:', filename);
        
        // Create image preview modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        
        // Use server endpoint to serve the image
        const imageUrl = `/api/file?path=${encodeURIComponent(path)}`;
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 90%; max-height: 90%;">
                <div class="modal-header">
                    <h3>Image Preview: ${filename}</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div style="padding: 2rem; text-align: center;">
                    <div style="margin-bottom: 1rem;">
                        <img src="${imageUrl}" 
                             alt="${filename}" 
                             style="max-width: 100%; max-height: 70vh; border: 1px solid #ddd; border-radius: 8px;"
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div style="display: none; padding: 2rem; color: #666;">
                            <p>Unable to preview image.</p>
                            <p style="margin-top: 1rem;">File location:</p>
                            <code style="background: #f5f5f5; padding: 1rem; border-radius: 4px; display: block; margin: 1rem 0; word-break: break-all;">${path}</code>
                            <button class="btn btn-primary" onclick="dashboard.revealInFinder('${path}')">Open in Finder</button>
                        </div>
                    </div>
                    <div class="asset-actions" style="justify-content: center;">
                        <button class="btn" onclick="dashboard.downloadFile('${path}', '${filename}')">Download</button>
                        <button class="btn" onclick="dashboard.revealInFinder('${path}')">Open in Finder</button>
                        <button class="btn" onclick="dashboard.copyPath('${path}')">Copy Path</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
            max-width: 300px;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };
        toast.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    getFileIcon(ext) {
        const iconPath = (iconName) => `<img src="icons/${iconName}.svg" alt="${ext}" style="width: 24px; height: 24px; filter: invert(32%) sepia(35%) saturate(1654%) hue-rotate(272deg) brightness(89%) contrast(92%);">`;
        
        const icons = {
            'png': iconPath('image'),
            'jpg': iconPath('image'), 
            'jpeg': iconPath('image'), 
            'gif': iconPath('image'),
            'ai': iconPath('image'),
            'psd': iconPath('image'), 
            'pdf': iconPath('file'),
            'docx': iconPath('file'), 
            'txt': iconPath('file'), 
            'indd': iconPath('file'),
            'zip': iconPath('package'), 
            'rar': iconPath('package')
        };
        return icons[ext] || iconPath('file');
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new PackagingDashboard();
});

// Add some CSS for the new elements
const style = document.createElement('style');
style.textContent = `
.asset-type-group {
    margin-bottom: 2rem;
}

.asset-type-header {
    color: var(--primary-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent-color);
}

.no-results {
    grid-column: 1 / -1;
    text-align: center;
    padding: 4rem;
    color: var(--text-secondary);
}

.error {
    text-align: center;
    padding: 2rem;
    color: var(--danger-color);
}

code {
    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}
`;
document.head.appendChild(style);