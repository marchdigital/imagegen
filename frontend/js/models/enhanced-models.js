// frontend/js/models/enhanced-models.js
// Support for WAN-25, Qwen Edit, and Product Photoshoot models

class EnhancedModelsAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || window.location.origin;
        this.apiBase = `${this.baseUrl}/api/extended`;
    }

    // WAN-25 Preview Generation
    async generateWAN25(settings) {
        const formData = new FormData();
        formData.append('settings', JSON.stringify(settings));

        const response = await fetch(`${this.apiBase}/wan25`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'WAN-25 generation failed');
        }

        return await response.json();
    }

    // Qwen Image Edit
    async editWithQwen(imageFile, maskFile, settings) {
        const formData = new FormData();
        formData.append('image', imageFile);
        if (maskFile) {
            formData.append('mask', maskFile);
        }
        formData.append('settings', JSON.stringify(settings));

        const response = await fetch(`${this.apiBase}/qwen-edit`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Qwen editing failed');
        }

        return await response.json();
    }

    // Product Photoshoot
    async generateProductShoot(productImages, settings) {
        const formData = new FormData();
        
        // Add multiple product images
        productImages.forEach((image, index) => {
            formData.append('product_images', image);
        });
        
        formData.append('settings', JSON.stringify(settings));

        const response = await fetch(`${this.apiBase}/product-photoshoot`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Product photoshoot failed');
        }

        return await response.json();
    }

    // Get available models
    async getModels() {
        const response = await fetch(`${this.apiBase}/models`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch models');
        }

        return await response.json();
    }

    // Helper function to convert blob URL to File
    async blobUrlToFile(blobUrl, fileName) {
        const response = await fetch(blobUrl);
        const blob = await response.blob();
        return new File([blob], fileName, { type: blob.type });
    }

    // Helper function to display results
    displayResults(results, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        if (results.images && results.images.length > 0) {
            results.images.forEach((image, index) => {
                const imgWrapper = document.createElement('div');
                imgWrapper.className = 'result-image-wrapper';
                
                const img = document.createElement('img');
                img.src = image.url || `data:image/png;base64,${image.data}`;
                img.className = 'result-image';
                img.alt = `Result ${index + 1}`;
                
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'btn btn-small';
                downloadBtn.textContent = 'Download';
                downloadBtn.onclick = () => this.downloadImage(img.src, `result_${index + 1}.png`);
                
                imgWrapper.appendChild(img);
                imgWrapper.appendChild(downloadBtn);
                container.appendChild(imgWrapper);
            });
        }
    }

    // Download helper
    downloadImage(url, filename) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// Initialize on page load
let enhancedAPI;

document.addEventListener('DOMContentLoaded', () => {
    enhancedAPI = new EnhancedModelsAPI();
    
    // Add event listeners for WAN-25 page
    if (document.getElementById('wan25-generate')) {
        document.getElementById('wan25-generate').addEventListener('click', async () => {
            const settings = {
                prompt: document.getElementById('wan25-prompt')?.value,
                aspect_ratio: document.getElementById('wan25-aspect')?.value || '1:1',
                output_format: document.getElementById('wan25-format')?.value || 'webp',
                quality: parseInt(document.getElementById('wan25-quality')?.value || 80),
                style: document.getElementById('wan25-style')?.value,
                negative_prompt: document.getElementById('wan25-negative')?.value,
                seed: document.getElementById('wan25-seed')?.value ? 
                      parseInt(document.getElementById('wan25-seed').value) : null
            };

            try {
                showLoading(true);
                const result = await enhancedAPI.generateWAN25(settings);
                enhancedAPI.displayResults(result.result, 'wan25-results');
                showSuccess('WAN-25 generation completed!');
            } catch (error) {
                showError(error.message);
            } finally {
                showLoading(false);
            }
        });
    }

    // Add event listeners for Qwen Edit page
    if (document.getElementById('qwen-edit-button')) {
        document.getElementById('qwen-edit-button').addEventListener('click', async () => {
            const imageInput = document.getElementById('qwen-image');
            const maskInput = document.getElementById('qwen-mask');
            
            if (!imageInput?.files[0]) {
                showError('Please select an image to edit');
                return;
            }

            const settings = {
                instruction: document.getElementById('qwen-instruction')?.value,
                edit_type: document.getElementById('qwen-edit-type')?.value || 'object',
                edit_strength: parseFloat(document.getElementById('qwen-strength')?.value || 0.8),
                coherence: parseFloat(document.getElementById('qwen-coherence')?.value || 0.7),
                auto_mask: document.getElementById('qwen-auto-mask')?.checked ?? true,
                preserve_style: document.getElementById('qwen-preserve-style')?.checked ?? true
            };

            try {
                showLoading(true);
                const result = await enhancedAPI.editWithQwen(
                    imageInput.files[0],
                    maskInput?.files[0],
                    settings
                );
                enhancedAPI.displayResults(result.result, 'qwen-results');
                showSuccess('Qwen editing completed!');
            } catch (error) {
                showError(error.message);
            } finally {
                showLoading(false);
            }
        });
    }

    // Add event listeners for Product Photoshoot page
    if (document.getElementById('product-generate')) {
        document.getElementById('product-generate').addEventListener('click', async () => {
            const imageInputs = document.getElementById('product-images');
            
            if (!imageInputs?.files || imageInputs.files.length === 0) {
                showError('Please select at least one product image');
                return;
            }

            const settings = {
                product_category: document.getElementById('product-category')?.value,
                product_description: document.getElementById('product-description')?.value,
                scene_type: document.getElementById('product-scene')?.value || 'studio',
                background_style: document.getElementById('product-background')?.value || 'gradient',
                lighting_setup: document.getElementById('product-lighting')?.value || 'soft',
                props: document.getElementById('product-props')?.value ? 
                       document.getElementById('product-props').value.split(',').map(p => p.trim()) : null,
                remove_background: document.getElementById('product-remove-bg')?.checked ?? false,
                preserve_shadows: document.getElementById('product-shadows')?.checked ?? true,
                color_palette: document.getElementById('product-palette')?.value,
                reflection_intensity: parseFloat(document.getElementById('product-reflection')?.value || 0),
                output_format: document.getElementById('product-format')?.value || 'png',
                resolution: document.getElementById('product-resolution')?.value || '1024x1024',
                batch_size: parseInt(document.getElementById('product-batch')?.value || 1),
                add_watermark: document.getElementById('product-watermark')?.checked ?? false,
                generate_variations: document.getElementById('product-variations')?.checked ?? false
            };

            try {
                showLoading(true);
                const productImages = Array.from(imageInputs.files);
                const result = await enhancedAPI.generateProductShoot(productImages, settings);
                enhancedAPI.displayResults(result.result, 'product-results');
                showSuccess('Product photoshoot completed!');
            } catch (error) {
                showError(error.message);
            } finally {
                showLoading(false);
            }
        });
    }
});

// UI Helper Functions
function showLoading(show) {
    const loadingElements = document.querySelectorAll('.loading, .loading-overlay');
    loadingElements.forEach(el => {
        if (show) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
    console.error(message);
}

function showNotification(message, type = 'info') {
    // Try to use existing notification system
    if (window.showNotification) {
        window.showNotification(message, type);
        return;
    }

    // Fallback notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#ff4444' : type === 'success' ? '#44ff44' : '#4444ff'};
        color: white;
        border-radius: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Export for use in other scripts
window.EnhancedModelsAPI = EnhancedModelsAPI;
window.enhancedAPI = enhancedAPI;
