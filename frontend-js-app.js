// frontend/js/app.js

class AIImageGenerator {
    constructor() {
        this.currentProvider = null;
        this.currentModel = null;
        this.providers = [];
        this.isGenerating = false;
        this.generationHistory = [];
        this.settings = {
            theme: 'dark',
            autoSave: true,
            confirmDelete: true,
            keyboardShortcuts: true
        };
        
        this.init();
    }
    
    async init() {
        console.log('Initializing AI Image Generator...');
        
        // Initialize API client
        this.api = new APIClient();
        
        // Initialize UI components
        this.ui = new UIManager(this);
        
        // Initialize generation manager
        this.generation = new GenerationManager(this);
        
        // Load initial data
        await this.loadProviders();
        await this.loadSettings();
        await this.loadRecentHistory();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup keyboard shortcuts
        if (this.settings.keyboardShortcuts) {
            this.setupKeyboardShortcuts();
        }
        
        console.log('Application initialized successfully');
    }
    
    async loadProviders() {
        try {
            this.providers = await this.api.getProviders();
            this.ui.populateProviders(this.providers);
            
            // Select first provider by default
            if (this.providers.length > 0) {
                this.selectProvider(this.providers[0].id);
            }
        } catch (error) {
            console.error('Failed to load providers:', error);
            this.ui.showError('Failed to load providers');
        }
    }
    
    async loadSettings() {
        try {
            const settings = await this.api.getSettings();
            this.settings = { ...this.settings, ...settings };
            this.ui.applySettings(this.settings);
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }
    
    async loadRecentHistory() {
        try {
            const history = await this.api.getRecentGenerations(10);
            this.generationHistory = history;
            this.ui.updateHistoryGallery(history);
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }
    
    selectProvider(providerId) {
        const provider = this.providers.find(p => p.id === parseInt(providerId));
        if (provider) {
            this.currentProvider = provider;
            this.ui.populateModels(provider.models);
            
            // Select first model
            if (provider.models.length > 0) {
                this.selectModel(provider.models[0].id);
            }
        }
    }
    
    selectModel(modelId) {
        const model = this.currentProvider?.models.find(m => m.id === parseInt(modelId));
        if (model) {
            this.currentModel = model;
            this.ui.updateModelCapabilities(model);
        }
    }
    
    async generateImage() {
        if (this.isGenerating) {
            this.ui.showWarning('Generation already in progress');
            return;
        }
        
        // Validate inputs
        const params = this.ui.getGenerationParams();
        if (!params.prompt) {
            this.ui.showError('Please enter a prompt');
            return;
        }
        
        if (!this.currentModel) {
            this.ui.showError('Please select a model');
            return;
        }
        
        this.isGenerating = true;
        this.ui.setGenerating(true);
        
        try {
            // Add model and provider info
            params.provider_id = this.currentProvider.id;
            params.model_id = this.currentModel.id;
            
            // Start generation
            const result = await this.api.generateImage(params);
            
            // Display result
            this.ui.displayGenerationResult(result);
            
            // Add to history
            this.generationHistory.unshift(result);
            this.ui.updateHistoryGallery(this.generationHistory);
            
            // Auto-save if enabled
            if (this.settings.autoSave) {
                await this.saveImage(result);
            }
            
            // Update stats
            await this.updateStats();
            
        } catch (error) {
            console.error('Generation failed:', error);
            this.ui.showError(`Generation failed: ${error.message}`);
        } finally {
            this.isGenerating = false;
            this.ui.setGenerating(false);
        }
    }
    
    async saveImage(generation) {
        try {
            // If running in desktop mode with pywebview
            if (window.pywebview && window.pywebview.api) {
                const filename = await window.pywebview.api.save_file_dialog(
                    `generation_${generation.id}.png`
                );
                if (filename) {
                    await this.api.saveImageToFile(generation.id, filename);
                    this.ui.showSuccess('Image saved successfully');
                }
            } else {
                // Web download
                const imageUrl = `/storage/images/${generation.image_path}`;
                const a = document.createElement('a');
                a.href = imageUrl;
                a.download = `generation_${generation.id}.png`;
                a.click();
            }
        } catch (error) {
            console.error('Failed to save image:', error);
            this.ui.showError('Failed to save image');
        }
    }
    
    async updateStats() {
        try {
            const stats = await this.api.getDashboardStats();
            this.ui.updateStatusBar(stats);
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }
    
    setupEventListeners() {
        // Provider selection
        document.getElementById('provider-select').addEventListener('change', (e) => {
            this.selectProvider(e.target.value);
        });
        
        // Model selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('model-card')) {
                document.querySelectorAll('.model-card').forEach(card => {
                    card.classList.remove('selected');
                });
                e.target.classList.add('selected');
                this.selectModel(e.target.dataset.modelId);
            }
        });
        
        // Generate button
        document.getElementById('btn-generate').addEventListener('click', () => {
            this.generateImage();
        });
        
        // Tab navigation
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.ui.switchTab(tabName);
            });
        });
        
        // Accordion toggles
        document.querySelectorAll('.accordion-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const item = e.currentTarget.parentElement;
                item.classList.toggle('active');
            });
        });
        
        // Sliders
        document.getElementById('steps').addEventListener('input', (e) => {
            document.getElementById('steps-value').textContent = e.target.value;
        });
        
        document.getElementById('cfg-scale').addEventListener('input', (e) => {
            document.getElementById('cfg-value').textContent = e.target.value;
        });
        
        document.getElementById('denoising').addEventListener('input', (e) => {
            document.getElementById('denoising-value').textContent = e.target.value;
        });
        
        // Aspect ratio changes
        document.getElementById('aspect-ratio').addEventListener('change', (e) => {
            this.ui.updateSizeFromAspectRatio(e.target.value);
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to generate
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.generateImage();
            }
            
            // Ctrl/Cmd + S to save current image
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                if (this.generationHistory.length > 0) {
                    this.saveImage(this.generationHistory[0]);
                }
            }
            
            // Ctrl/Cmd + R for random seed
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                document.getElementById('seed').value = -1;
            }
            
            // Escape to cancel generation
            if (e.key === 'Escape' && this.isGenerating) {
                this.cancelGeneration();
            }
        });
    }
    
    async cancelGeneration() {
        if (this.isGenerating) {
            try {
                await this.api.cancelGeneration();
                this.isGenerating = false;
                this.ui.setGenerating(false);
                this.ui.showInfo('Generation cancelled');
            } catch (error) {
                console.error('Failed to cancel generation:', error);
            }
        }
    }
}

// API Client Class
class APIClient {
    constructor() {
        this.baseUrl = '/api';
    }
    
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        
        return response.json();
    }
    
    async getProviders() {
        return this.request('/providers');
    }
    
    async getSettings() {
        return this.request('/settings');
    }
    
    async generateImage(params) {
        return this.request('/generation/generate', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
    
    async getRecentGenerations(limit = 10) {
        return this.request(`/gallery?limit=${limit}`);
    }
    
    async getDashboardStats() {
        return this.request('/dashboard/stats');
    }
    
    async cancelGeneration(generationId) {
        return this.request(`/generation/cancel/${generationId}`, {
            method: 'POST'
        });
    }
    
    async saveImageToFile(generationId, filepath) {
        return this.request('/gallery/save', {
            method: 'POST',
            body: JSON.stringify({ generation_id: generationId, filepath })
        });
    }
}

// UI Manager Class
class UIManager {
    constructor(app) {
        this.app = app;
    }
    
    populateProviders(providers) {
        const select = document.getElementById('provider-select');
        select.innerHTML = '';
        
        providers.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider.id;
            option.textContent = provider.name;
            select.appendChild(option);
        });
    }
    
    populateModels(models) {
        const grid = document.getElementById('model-grid');
        grid.innerHTML = '';
        
        models.forEach(model => {
            const card = document.createElement('div');
            card.className = 'model-card';
            card.dataset.modelId = model.id;
            card.textContent = model.display_name || model.name;
            grid.appendChild(card);
        });
        
        // Select first model
        if (models.length > 0) {
            grid.firstElementChild.classList.add('selected');
        }
    }
    
    updateModelCapabilities(model) {
        // Update UI based on model capabilities
        const img2imgAccordion = document.querySelector('.accordion-item:nth-child(2)');
        if (!model.supports_img2img) {
            img2imgAccordion.style.display = 'none';
        } else {
            img2imgAccordion.style.display = 'block';
        }
        
        // Update max dimensions
        document.getElementById('width').max = model.max_width;
        document.getElementById('height').max = model.max_height;
    }
    
    getGenerationParams() {
        return {
            prompt: document.getElementById('prompt').value,
            negative_prompt: document.getElementById('negative-prompt').value,
            width: parseInt(document.getElementById('width').value),
            height: parseInt(document.getElementById('height').value),
            steps: parseInt(document.getElementById('steps').value),
            cfg_scale: parseFloat(document.getElementById('cfg-scale').value),
            seed: parseInt(document.getElementById('seed').value),
            sampler: document.getElementById('sampler').value,
            batch_size: parseInt(document.getElementById('batch-size').value),
            denoising_strength: parseFloat(document.getElementById('denoising').value)
        };
    }
    
    setGenerating(isGenerating) {
        const button = document.getElementById('btn-generate');
        const spinner = document.getElementById('generation-spinner');
        const message = document.getElementById('preview-message');
        
        if (isGenerating) {
            button.disabled = true;
            button.textContent = '⏳ Generating...';
            spinner.style.display = 'block';
            message.style.display = 'none';
        } else {
            button.disabled = false;
            button.textContent = '🚀 Generate Image';
            spinner.style.display = 'none';
            message.style.display = 'block';
        }
    }
    
    displayGenerationResult(result) {
        const placeholder = document.getElementById('preview-placeholder');
        const image = document.getElementById('preview-image');
        const actions = document.getElementById('preview-actions');
        
        placeholder.style.display = 'none';
        image.src = `/storage/images/${result.image_path}`;
        image.style.display = 'block';
        actions.style.display = 'flex';
    }
    
    updateHistoryGallery(history) {
        const gallery = document.getElementById('recent-gallery');
        gallery.innerHTML = '';
        
        history.slice(0, 6).forEach(item => {
            const div = document.createElement('div');
            div.className = 'gallery-item';
            div.innerHTML = `
                <img src="/storage/thumbnails/thumb_${item.image_path}" alt="">
                <div class="gallery-item-info">
                    ${item.model_name} • ${this.timeAgo(item.created_at)}
                </div>
            `;
            gallery.appendChild(div);
        });
    }
    
    updateStatusBar(stats) {
        document.getElementById('generation-count').textContent = stats.total_generations;
        document.getElementById('last-generation-time').textContent = 
            stats.last_generation ? `${stats.last_generation.time}s` : '--';
        document.getElementById('storage-usage').textContent = 
            `${stats.storage_usage_gb} GB`;
    }
    
    updateSizeFromAspectRatio(ratio) {
        const width = document.getElementById('width');
        const height = document.getElementById('height');
        
        switch(ratio) {
            case '1:1':
                width.value = 1024;
                height.value = 1024;
                break;
            case '16:9':
                width.value = 1024;
                height.value = 576;
                break;
            case '9:16':
                width.value = 576;
                height.value = 1024;
                break;
            case '4:3':
                width.value = 1024;
                height.value = 768;
                break;
        }
    }
    
    applySettings(settings) {
        // Apply theme
        if (settings.theme === 'light') {
            document.body.classList.add('light-theme');
        }
    }
    
    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Load tab content (to be implemented)
        console.log(`Switching to tab: ${tabName}`);
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showWarning(message) {
        this.showNotification(message, 'warning');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 6px;
            background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4CAF50' : '#2196F3'};
            color: white;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    timeAgo(timestamp) {
        const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
        
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
        return `${Math.floor(seconds / 86400)} days ago`;
    }
}

// Generation Manager Class
class GenerationManager {
    constructor(app) {
        this.app = app;
        this.currentGenerationId = null;
    }
    
    // Additional generation-related methods...
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AIImageGenerator();
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification {
        transition: all 0.3s ease;
    }
    
    .light-theme {
        --bg-primary: #ffffff;
        --bg-secondary: #f5f5f5;
        --bg-tertiary: #e0e0e0;
        --text-primary: #212121;
        --text-secondary: #757575;
        --border: #ddd;
    }
`;
document.head.appendChild(style);