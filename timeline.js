/**
 * Vital Planet Packaging Timeline
 * JavaScript for the timeline view interface
 */

class TimelineDashboard {
    constructor() {
        this.allEvents = [];
        this.filteredEvents = [];
        this.currentFilters = {
            search: '',
            dateRange: 'week',
            productLine: 'all',
            assetType: 'all',
            status: 'all'
        };
        
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadTimelineData();
        this.updateStats();
        this.renderTimeline();
    }

    bindEvents() {
        // Search functionality
        document.getElementById('timelineSearch').addEventListener('input', () => {
            this.currentFilters.search = document.getElementById('timelineSearch').value;
            this.filterEvents();
        });

        document.getElementById('clearTimelineSearch').addEventListener('click', () => {
            document.getElementById('timelineSearch').value = '';
            this.currentFilters.search = '';
            this.filterEvents();
        });

        // Filter dropdowns
        document.getElementById('dateRangeFilter').addEventListener('change', (e) => {
            this.currentFilters.dateRange = e.target.value;
            this.filterEvents();
        });

        document.getElementById('productLineFilter').addEventListener('change', (e) => {
            this.currentFilters.productLine = e.target.value;
            this.filterEvents();
        });

        document.getElementById('assetTypeFilter').addEventListener('change', (e) => {
            this.currentFilters.assetType = e.target.value;
            this.filterEvents();
        });

        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.currentFilters.status = e.target.value;
            this.filterEvents();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && !e.target.matches('input, textarea')) {
                e.preventDefault();
                document.getElementById('timelineSearch').focus();
            }
        });
    }

    async loadTimelineData() {
        try {
            document.getElementById('timelineLoading').style.display = 'block';
            
            const response = await fetch('/api/timeline');
            if (!response.ok) throw new Error('Failed to load timeline data');
            
            const data = await response.json();
            this.allEvents = data.events || [];
            this.filteredEvents = [...this.allEvents];
            
            document.getElementById('timelineLoading').style.display = 'none';
            document.getElementById('timelineContent').style.display = 'block';
            
        } catch (error) {
            console.error('Error loading timeline data:', error);
            document.getElementById('timelineLoading').innerHTML = `
                <div class="error">
                    <p>Error loading timeline data. Please try refreshing the page.</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }

    filterEvents() {
        let filtered = [...this.allEvents];
        
        // Search filter
        if (this.currentFilters.search) {
            const search = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(event => 
                event.asset_name.toLowerCase().includes(search) ||
                event.product_name.toLowerCase().includes(search) ||
                event.product_code.toLowerCase().includes(search) ||
                event.asset_type.toLowerCase().includes(search)
            );
        }
        
        // Date range filter
        const now = new Date();
        const filterDate = this.getFilterDate(this.currentFilters.dateRange, now);
        if (filterDate) {
            filtered = filtered.filter(event => new Date(event.date) >= filterDate);
        }
        
        // Product line filter
        if (this.currentFilters.productLine !== 'all') {
            filtered = filtered.filter(event => event.product_line === this.currentFilters.productLine);
        }
        
        // Asset type filter
        if (this.currentFilters.assetType !== 'all') {
            filtered = filtered.filter(event => event.asset_type === this.currentFilters.assetType);
        }
        
        // Status filter
        if (this.currentFilters.status !== 'all') {
            filtered = filtered.filter(event => event.status === this.currentFilters.status);
        }
        
        this.filteredEvents = filtered;
        this.updateStats();
        this.renderTimeline();
    }

    getFilterDate(range, now) {
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        
        switch (range) {
            case 'today':
                return today;
            case 'yesterday':
                return new Date(today.getTime() - 24 * 60 * 60 * 1000);
            case 'week':
                return new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            case 'month':
                return new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            case 'quarter':
                return new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
            case 'year':
                return new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);
            case 'all':
            default:
                return null;
        }
    }

    updateStats() {
        const totalEvents = this.filteredEvents.length;
        document.getElementById('totalEvents').textContent = `${totalEvents.toLocaleString()} Events`;
        
        if (totalEvents > 0) {
            const latestDate = new Date(this.filteredEvents[0].date);
            const oldestDate = new Date(this.filteredEvents[this.filteredEvents.length - 1].date);
            const range = this.formatDateRange(oldestDate, latestDate);
            document.getElementById('dateRange').textContent = range;
        } else {
            document.getElementById('dateRange').textContent = 'No events';
        }
    }

    formatDateRange(startDate, endDate) {
        const options = { month: 'short', day: 'numeric', year: 'numeric' };
        const start = startDate.toLocaleDateString('en-US', options);
        const end = endDate.toLocaleDateString('en-US', options);
        
        if (start === end) {
            return start;
        }
        return `${start} - ${end}`;
    }

    renderTimeline() {
        const container = document.getElementById('timelineEvents');
        const noResults = document.getElementById('noTimelineResults');
        
        if (this.filteredEvents.length === 0) {
            container.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }
        
        noResults.style.display = 'none';
        
        // Group events by date
        const groupedEvents = this.groupEventsByDate(this.filteredEvents);
        
        const html = Object.entries(groupedEvents)
            .map(([dateGroup, events]) => this.renderDateGroup(dateGroup, events))
            .join('');
        
        container.innerHTML = html;
    }

    groupEventsByDate(events) {
        const groups = {};
        const now = new Date();
        
        events.forEach(event => {
            const eventDate = new Date(event.date);
            const dateKey = this.getDateGroupKey(eventDate, now);
            
            if (!groups[dateKey]) {
                groups[dateKey] = [];
            }
            groups[dateKey].push(event);
        });
        
        return groups;
    }

    getDateGroupKey(eventDate, now) {
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
        const eventDateOnly = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());
        
        if (eventDateOnly.getTime() === today.getTime()) {
            return 'Today';
        } else if (eventDateOnly.getTime() === yesterday.getTime()) {
            return 'Yesterday';
        } else if (eventDateOnly.getTime() > today.getTime() - 7 * 24 * 60 * 60 * 1000) {
            return `This Week - ${eventDate.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}`;
        } else if (eventDateOnly.getFullYear() === now.getFullYear()) {
            return eventDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
        } else {
            return eventDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
        }
    }

    renderDateGroup(dateGroup, events) {
        const eventsHtml = events.map(event => this.renderTimelineEvent(event)).join('');
        
        return `
            <div class="timeline-date-group">
                <h3 class="timeline-date-header">${dateGroup} (${events.length})</h3>
                <div class="timeline-events-list">
                    ${eventsHtml}
                </div>
            </div>
        `;
    }

    renderTimelineEvent(event) {
        const eventDate = new Date(event.date);
        const timeString = eventDate.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        
        const fileSize = this.formatFileSize(event.file_size);
        const isImage = ['png', 'jpg', 'jpeg', 'gif'].includes(event.file_extension.replace('.', '').toLowerCase());
        const isGrouped = event.is_grouped || false;
        
        // Get appropriate icon based on asset type
        const icon = this.getAssetTypeIcon(event.asset_type);
        
        // Create format badges for grouped assets
        const formatBadges = isGrouped && event.available_formats ? 
            event.available_formats.map(format => 
                `<span class="format-badge format-${format.toLowerCase()}">${format}</span>`
            ).join('') : '';
        
        return `
            <div class="timeline-event ${isGrouped ? 'timeline-event-grouped' : ''}" data-product="${event.product_code}">
                <div class="timeline-event-icon">
                    ${icon}
                </div>
                <div class="timeline-event-content">
                    <div class="timeline-event-header">
                        <div class="timeline-event-time">${timeString}</div>
                        <div class="timeline-event-product">
                            <span class="product-code">${event.product_code}</span>
                            <span class="product-name">${this.truncateText(event.product_name, 40)}</span>
                        </div>
                    </div>
                    <div class="timeline-event-details">
                        <div class="asset-name">${event.asset_name}${isGrouped ? ` (${event.total_assets} formats)` : ''}</div>
                        <div class="timeline-event-meta">
                            <span class="asset-type-badge">${event.asset_type}</span>
                            ${isGrouped ? formatBadges : `<span class="file-ext-badge">${event.file_extension.replace('.', '').toUpperCase()}</span>`}
                            <span class="file-size">${fileSize}</span>
                            <span class="product-line-badge ${event.product_line.toLowerCase()}">${event.product_line}</span>
                            ${event.status !== 'Current' ? `<span class="status-badge">${event.status}</span>` : ''}
                        </div>
                    </div>
                    <div class="timeline-event-actions">
                        ${isImage ? `
                            <button class="btn btn-small btn-primary" onclick="timeline.previewAsset('${event.full_path}', '${event.asset_name}')">
                                Preview
                            </button>
                        ` : ''}
                        <button class="btn btn-small" onclick="timeline.viewProduct('${event.product_code}')">
                            View Product
                        </button>
                        <button class="btn btn-small" onclick="timeline.downloadAsset('${event.full_path}', '${event.asset_name}')">
                            Download
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getAssetTypeIcon(assetType) {
        // Use our icon system
        switch (assetType) {
            case '3D Mockup':
                return '<img src="icons/package.svg" alt="3D Mockup" style="width: 32px; height: 32px; filter: invert(32%) sepia(35%) saturate(1654%) hue-rotate(272deg) brightness(89%) contrast(92%);">';
            case 'Box Art':
                return '<img src="icons/image.svg" alt="Box Art" style="width: 32px; height: 32px; filter: invert(32%) sepia(35%) saturate(1654%) hue-rotate(272deg) brightness(89%) contrast(92%);">';
            case 'Label Art':
                return '<img src="icons/image.svg" alt="Label Art" style="width: 32px; height: 32px; filter: invert(32%) sepia(35%) saturate(1654%) hue-rotate(272deg) brightness(89%) contrast(92%);">';
            case 'Print Ready':
                return '<img src="icons/file.svg" alt="Print Ready" style="width: 32px; height: 32px; filter: invert(32%) sepia(35%) saturate(1654%) hue-rotate(272deg) brightness(89%) contrast(92%);">';
            default:
                return '<img src="icons/file.svg" alt="File" style="width: 32px; height: 32px; filter: invert(32%) sepia(35%) saturate(1654%) hue-rotate(272deg) brightness(89%) contrast(92%);">';
        }
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

    // Action methods
    previewAsset(path, filename) {
        // Use same preview logic as main dashboard
        const imageUrl = `/api/file?path=${encodeURIComponent(path)}`;
        const modal = document.createElement('div');
        modal.className = 'modal';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 90%; max-height: 90%;">
                <div class="modal-header">
                    <h3>Image Preview: ${filename}</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div style="padding: 2rem; text-align: center;">
                    <img src="${imageUrl}" alt="${filename}" 
                         style="max-width: 100%; max-height: 70vh; border: 1px solid #ddd; border-radius: 8px;">
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    downloadAsset(path, filename) {
        const downloadUrl = `/api/download?path=${encodeURIComponent(path)}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    viewProduct(productCode) {
        // Navigate back to main dashboard with product focus
        window.location.href = `/?product=${productCode}`;
    }
}

// Initialize timeline when page loads
let timeline;
document.addEventListener('DOMContentLoaded', () => {
    timeline = new TimelineDashboard();
});