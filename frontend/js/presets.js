// Add this to your main JavaScript
async function loadPresets() {
    try {
        const response = await fetch('/storage/presets.json');
        const data = await response.json();
        
        const presetSelect = document.getElementById('preset-select');
        if (!presetSelect) {
            // Create preset selector if it doesn't exist
            const presetHtml = `
                <div class="form-group">
                    <label>Style Preset</label>
                    <select id="preset-select" style="width: 100%;">
                        <option value="">-- No Preset --</option>
                    </select>
                </div>
            `;
            // Insert after model selection
            document.querySelector('.sidebar').insertAdjacentHTML('beforeend', presetHtml);
        }
        
        const select = document.getElementById('preset-select');
        data.presets.forEach(preset => {
            const option = document.createElement('option');
            option.value = preset.id;
            option.textContent = preset.name;
            option.dataset.preset = JSON.stringify(preset);
            select.appendChild(option);
        });
        
        // Handle preset selection
        select.onchange = function() {
            if (this.value) {
                const preset = JSON.parse(this.selectedOptions[0].dataset.preset);
                applyPreset(preset);
            }
        };
    } catch (error) {
        console.error('Failed to load presets:', error);
    }
}

function applyPreset(preset) {
    // Update prompt with suffix
    const promptField = document.getElementById('prompt');
    const currentPrompt = promptField.value;
    
    // Remove any existing preset suffix (starts with ", ")
    const basePrompt = currentPrompt.split(', ')[0];
    promptField.value = basePrompt + preset.prompt_suffix;
    
    // Update negative prompt
    document.getElementById('negative-prompt').value = preset.negative_prompt;
    
    // Update generation parameters
    if (document.getElementById('cfg-scale')) {
        document.getElementById('cfg-scale').value = preset.cfg_scale;
        document.getElementById('cfg-value').textContent = preset.cfg_scale;
    }
    
    if (document.getElementById('steps')) {
        document.getElementById('steps').value = preset.steps;
        document.getElementById('steps-value').textContent = preset.steps;
    }
    
    // Visual feedback
    showNotification(`Applied preset: ${preset.name}`, 'success');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4CAF50' : '#2196F3'};
        color: white;
        border-radius: 4px;
        z-index: 1000;
        animation: slideIn 0.3s;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
}

// Load presets on page load
document.addEventListener('DOMContentLoaded', loadPresets);
