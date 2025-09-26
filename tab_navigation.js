// Add this JavaScript to your main HTML to handle tab switching
function initializeTabs() {
    // Create tab structure
    const tabsHtml = `
        <div class="tabs" style="display: flex; background: #242424; border-bottom: 1px solid #333;">
            <button class="tab-btn active" data-view="generator" style="padding: 15px 25px; background: transparent; border: none; color: white; cursor: pointer; border-bottom: 2px solid #4CAF50;">
                🎨 Generator
            </button>
            <button class="tab-btn" data-view="gallery" style="padding: 15px 25px; background: transparent; border: none; color: #888; cursor: pointer;">
                🖼️ Gallery
            </button>
            <button class="tab-btn" data-view="dashboard" style="padding: 15px 25px; background: transparent; border: none; color: #888; cursor: pointer;">
                📊 Dashboard
            </button>
            <button class="tab-btn" data-view="settings" style="padding: 15px 25px; background: transparent; border: none; color: #888; cursor: pointer;">
                ⚙️ Settings
            </button>
        </div>
    `;
    
    // Add tabs to header
    const header = document.querySelector('.header');
    header.insertAdjacentHTML('beforeend', tabsHtml);
    
    // Handle tab clicks
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = function() {
            // Update active state
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('active');
                b.style.color = '#888';
                b.style.borderBottom = 'none';
            });
            this.classList.add('active');
            this.style.color = 'white';
            this.style.borderBottom = '2px solid #4CAF50';
            
            // Switch view
            const view = this.dataset.view;
            if (view === 'dashboard') {
                window.location.href = '/static/dashboard.html';
            } else if (view === 'gallery') {
                showGalleryView();
            } else if (view === 'settings') {
                showSettingsView();
            } else {
                showGeneratorView();
            }
        };
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializeTabs);
