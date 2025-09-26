// frontend/js/models/fal_models.js

class FalModelsManager {
    constructor() {
        this.apiBase = '/api/generate';
        this.currentModel = null;
        this.uploadedFiles = {
            main: null,
            references: [],
            mask: null,
            products: []
        };
    }

    // Initialize model interfaces
    init() {
        this.setupModelSelector();
        this.setupFileUploads();
        this.setupSliders();
        this.setupGenerateButtons();
        this.loadAvailableModels();
    }

    // Load available models from API
    async loadAvailableModels() {
        try {
            const response = await fetch(`${this.apiBase}/models`);
            const data = await response.json();
            this.renderModelCards(data.models);
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }

    // Render model selection cards
    renderModelCards(models) {
        const container = document.getElementById('model-selector');
        if (!container) return;

        models.forEach(model => {
            const card = this.createModelCard(model);
            container.appendChild(card);
        });
    }

    createModelCard(model) {
        const card = document.createElement('div');
        card.className = 'model-card';
        card.dataset.modelId = model.id;
        
        card.innerHTML = `
            <div class="model-card-header">
                <h4>${model.name}</h4>
                <span class="model-category">${model.category}</span>
            </div>
            <p class="model-description">${model.description}</p>
            <div class="model-features">
                ${model.features.map(f => `<span class="feature-tag">${f}</span>`).join('')}
            </div>
        `;
        
        card.addEventListener('click', () => this.selectModel(model.id));
        return card;
    }

    // Model selection
    selectModel(modelId) {
        this.currentModel = modelId;
        
        // Update UI
        document.querySelectorAll('.model-card').forEach(card => {
            card.classList.toggle('active', card.dataset.modelId === modelId);
        });
        
        // Show appropriate interface
        this.showModelInterface(modelId);
    }

    showModelInterface(modelId) {
        // Hide all interfaces
        document.querySelectorAll('.model-interface').forEach(interface => {
            interface.style.display = 'none';
        });
        
        // Show selected interface
        const interfaceId = `${modelId}-interface`;
        const modelInterface = document.getElementById(interfaceId);
        if (modelInterface) {
            modelInterface.style.display = 'block';
        }
    }

    // File upload handling
    setupFileUploads() {
        // WAN-25 main image upload
        this.setupDropZone('wan25-main-upload', (file) => {
            this.uploadedFiles.main = file;
            this.previewImage(file, 'wan25-main-preview');
        });
        
        // WAN-25 reference images
        this.setupMultiUpload('wan25-references', (files) => {
            this.uploadedFiles.references = files;
            this.previewMultipleImages(files, 'wan25-ref-previews');
        });
        
        // Qwen edit image upload
        this.setupDropZone('qwen-image-upload', (file) => {
            this.uploadedFiles.main = file;
            this.previewImage(file, 'qwen-image-preview');
        });
        
        // Qwen mask upload
        this.setupDropZone('qwen-mask-upload', (file) => {
            this.uploadedFiles.mask = file;
            this.previewImage(file, 'qwen-mask-preview');
        });
        
        // Product images upload
        this.setupMultiUpload('product-images', (files) => {
            this.uploadedFiles.products = files;
            this.previewProductImages(files);
        });
    }

    setupDropZone(elementId, onFileSelect) {
        const dropZone = document.getElementById(elementId);
        if (!dropZone) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                onFileSelect(files[0]);
            }
        });
        
        // Handle click to select
        dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = (e) => {
                if (e.target.files.length > 0) {
                    onFileSelect(e.target.files[0]);
                }
            };
            input.click();
        });
    }

    setupMultiUpload(elementId, onFilesSelect) {
        const container = document.getElementById(elementId);
        if (!container) return;
        
        const uploadItems = container.querySelectorAll('.upload-item');
        uploadItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.multiple = true;
                input.onchange = (e) => {
                    const files = Array.from(e.target.files);
                    onFilesSelect(files);
                };
                input.click();
            });
        });
    }

    // Image preview
    previewImage(file, previewId) {
        const preview = document.getElementById(previewId);
        if (!preview) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview" style="max-width: 100%; max-height: 200px;">
                <div class="preview-info">
                    <small>${file.name}</small>
                    <small>${(file.size / 1024).toFixed(2)} KB</small>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }

    previewMultipleImages(files, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        files.forEach((file, index) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            
            const reader = new FileReader();
            reader.onload = (e) => {
                previewItem.innerHTML = `
                    <img src="${e.target.result}" alt="Reference ${index + 1}">
                    <button class="remove-btn" data-index="${index}">×</button>
                `;
                
                // Add remove functionality
                previewItem.querySelector('.remove-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.removeReferenceImage(index);
                });
            };
            reader.readAsDataURL(file);
            
            container.appendChild(previewItem);
        });
    }

    previewProductImages(files) {
        const container = document.getElementById('product-previews');
        if (!container) return;
        
        container.innerHTML = '';
        const viewTypes = ['Front View', 'Side View', 'Back View', 'Detail Shot'];
        
        files.forEach((file, index) => {
            const previewCard = document.createElement('div');
            previewCard.className = 'product-preview-card';
            
            const reader = new FileReader();
            reader.onload = (e) => {
                previewCard.innerHTML = `
                    <img src="${e.target.result}" alt="${viewTypes[index] || 'Product Image'}">
                    <div class="preview-label">${viewTypes[index] || `Image ${index + 1}`}</div>
                    <button class="remove-btn" data-index="${index}">×</button>
                `;
                
                previewCard.querySelector('.remove-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.removeProductImage(index);
                });
            };
            reader.readAsDataURL(file);
            
            container.appendChild(previewCard);
        });
    }

    removeReferenceImage(index) {
        this.uploadedFiles.references.splice(index, 1);
        this.previewMultipleImages(this.uploadedFiles.references, 'wan25-ref-previews');
    }

    removeProductImage(index) {
        this.uploadedFiles.products.splice(index, 1);
        this.previewProductImages(this.uploadedFiles.products);
    }

    // Slider setup
    setupSliders() {
        document.querySelectorAll('.slider-control').forEach(slider => {
            const valueDisplay = slider.parentElement.querySelector('.slider-value');
            
            slider.addEventListener('input', (e) => {
                if (valueDisplay) {
                    valueDisplay.textContent = e.target.value;
                }
            });
        });
    }

    // Generate button handlers
    setupGenerateButtons() {
        // WAN-25 Generate
        const wan25Btn = document.getElementById('generate-wan25');
        if (wan25Btn) {
            wan25Btn.addEventListener('click', () => this.generateWAN25());
        }
        
        // Qwen Edit
        const qwenBtn = document.getElementById('apply-qwen-edit');
        if (qwenBtn) {
            qwenBtn.addEventListener('click', () => this.applyQwenEdit());
        }
        
        // Product Photoshoot
        const productBtn = document.getElementById('generate-product-shots');
        if (productBtn) {
            productBtn.addEventListener('click', () => this.generateProductShots());
        }
    }

    // Generation methods
    async generateWAN25() {
        if (!this.uploadedFiles.main) {
            alert('Please upload a main image');
            return;
        }
        
        const formData = new FormData();
        formData.append('main_image', this.uploadedFiles.main);
        
        // Add reference images
        this.uploadedFiles.references.forEach(ref => {
            formData.append('reference_images', ref);
        });
        
        // Collect settings
        const settings = {
            prompt: document.getElementById('wan25-prompt').value,
            image_influence: parseFloat(document.getElementById('wan25-influence').value),
            style_strength: parseFloat(document.getElementById('wan25-style').value),
            aspect_ratio: document.getElementById('wan25-aspect').value,
            output_size: document.getElementById('wan25-size').value,
            guidance_scale: parseFloat(document.getElementById('wan25-guidance').value),
            seed: parseInt(document.getElementById('wan25-seed').value) || -1,
            hd_output: document.getElementById('wan25-hd').checked,
            auto_enhance: document.getElementById('wan25-enhance').checked
        };
        
        formData.append('settings', JSON.stringify(settings));
        
        // Show loading state
        this.showLoading('wan25-result');
        
        try {
            const response = await fetch(`${this.apiBase}/wan25-preview`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.displayResult(result, 'wan25-result');
        } catch (error) {
            this.showError(error, 'wan25-result');
        }
    }

    async applyQwenEdit() {
        if (!this.uploadedFiles.main) {
            alert('Please upload an image to edit');
            return;
        }
        
        const formData = new FormData();
        formData.append('image', this.uploadedFiles.main);
        
        if (this.uploadedFiles.mask) {
            formData.append('mask', this.uploadedFiles.mask);
        }
        
        const settings = {
            instruction: document.getElementById('qwen-instruction').value,
            edit_type: document.getElementById('qwen-edit-type').value,
            edit_strength: parseFloat(document.getElementById('qwen-strength').value),
            coherence: parseFloat(document.getElementById('qwen-coherence').value),
            auto_mask: document.getElementById('qwen-auto-mask').checked,
            preserve_style: document.getElementById('qwen-preserve-style').checked
        };
        
        formData.append('settings', JSON.stringify(settings));
        
        this.showLoading('qwen-result');
        
        try {
            const response = await fetch(`${this.apiBase}/qwen-edit`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.displayResult(result, 'qwen-result');
        } catch (error) {
            this.showError(error, 'qwen-result');
        }
    }

    async generateProductShots() {
        if (this.uploadedFiles.products.length === 0) {
            alert('Please upload at least one product image');
            return;
        }
        
        const formData = new FormData();
        
        this.uploadedFiles.products.forEach(img => {
            formData.append('product_images', img);
        });
        
        // Collect all settings
        const settings = {
            product_category: document.getElementById('product-category').value,
            product_description: document.getElementById('product-description').value,
            scene_type: document.querySelector('.scene-tag.active')?.dataset.scene || 'studio',
            background_style: document.getElementById('background-style').value,
            lighting_setup: document.getElementById('lighting-setup').value,
            props: document.getElementById('product-props').value,
            remove_background: document.getElementById('remove-bg').checked,
            preserve_shadows: document.getElementById('preserve-shadows').checked,
            reflection_intensity: parseFloat(document.getElementById('reflection').value),
            output_format: document.getElementById('output-format').value,
            resolution: document.getElementById('resolution').value,
            batch_size: parseInt(document.getElementById('batch-size').value),
            add_watermark: document.getElementById('add-watermark').checked,
            generate_variations: document.getElementById('gen-variations').checked
        };
        
        // Add color palette if selected
        const colorPalette = [];
        document.querySelectorAll('.color-picker.selected').forEach(picker => {
            colorPalette.push(picker.dataset.color);
        });
        if (colorPalette.length > 0) {
            settings.color_palette = colorPalette;
        }
        
        formData.append('settings', JSON.stringify(settings));
        
        this.showLoading('product-results');
        
        try {
            const response = await fetch(`${this.apiBase}/product-photoshoot`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.displayProductResults(result, 'product-results');
        } catch (error) {
            this.showError(error, 'product-results');
        }
    }

    // Display results
    displayResult(result, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="result-container">
                <img src="${result.result.image.url}" alt="Generated Image" class="result-image">
                <div class="result-actions">
                    <button class="btn-download" onclick="downloadImage('${result.result.image.url}')">
                        <i class="icon-download"></i> Download
                    </button>
                    <button class="btn-save" onclick="saveToGallery('${result.generation_id}')">
                        <i class="icon-save"></i> Save to Gallery
                    </button>
                    <button class="btn-regenerate" onclick="regenerate('${result.generation_id}')">
                        <i class="icon-refresh"></i> Regenerate
                    </button>
                </div>
                <div class="result-meta">
                    <small>Generation ID: ${result.generation_id}</small>
                </div>
            </div>
        `;
    }

    displayProductResults(result, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const images = result.result.images || [];
        
        container.innerHTML = `
            <div class="product-results-grid">
                ${images.map((img, index) => `
                    <div class="product-result-item">
                        <img src="${img.url}" alt="Product Shot ${index + 1}">
                        <div class="result-overlay">
                            <button class="btn-download" onclick="downloadImage('${img.url}')">
                                <i class="icon-download"></i>
                            </button>
                            <button class="btn-favorite" onclick="toggleFavorite('${img.id}')">
                                <i class="icon-star"></i>
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="batch-actions">
                <button class="btn-download-all">Download All (${images.length})</button>
                <button class="btn-save-project">Save to Project</button>
            </div>
        `;
    }

    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Generating... This may take a moment</p>
            </div>
        `;
    }

    showError(error, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="error-state">
                <i class="icon-error"></i>
                <p>Generation failed: ${error.message}</p>
                <button onclick="location.reload()">Try Again</button>
            </div>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const manager = new FalModelsManager();
    manager.init();
    
    // Export to global scope for other scripts
    window.falModelsManager = manager;
});

// Helper functions
function downloadImage(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated_${Date.now()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function saveToGallery(generationId) {
    fetch(`/api/gallery/save/${generationId}`, { method: 'POST' })
        .then(() => {
            alert('Saved to gallery!');
        })
        .catch(error => {
            alert('Failed to save: ' + error.message);
        });
}

function regenerate(generationId) {
    // Reload with same settings
    window.falModelsManager.regenerateWithSettings(generationId);
}