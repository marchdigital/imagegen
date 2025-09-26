// Add this JavaScript function to handle image uploads
function setupImageUpload() {
    const uploadArea = document.createElement('div');
    uploadArea.innerHTML = `
        <div class="accordion-item">
            <div class="accordion-header">
                <span>🖼️ Image-to-Image</span>
                <span>▼</span>
            </div>
            <div class="accordion-content">
                <div id="upload-area" style="border: 2px dashed #444; border-radius: 4px; padding: 30px; text-align: center; cursor: pointer;">
                    <p>📁 Drop image here or click to browse</p>
                    <input type="file" id="init-image" accept="image/*" style="display: none;">
                    <img id="init-preview" style="max-width: 100%; max-height: 200px; display: none; margin-top: 10px;">
                </div>
                
                <div class="slider-group" style="margin-top: 15px;">
                    <div class="slider-label">
                        <label>Denoising Strength</label>
                        <span id="denoising-value">0.75</span>
                    </div>
                    <input type="range" id="denoising" min="0" max="1" step="0.05" value="0.75">
                </div>
                
                <button class="btn btn-secondary" onclick="clearInitImage()" style="width: 100%; margin-top: 10px; display: none;" id="clear-image-btn">
                    Clear Image
                </button>
            </div>
        </div>
    `;
    
    // Insert after batch generation
    const accordion = document.querySelector('.accordion');
    accordion.appendChild(uploadArea);
    
    // Setup handlers
    const uploadAreaEl = document.getElementById('upload-area');
    const fileInput = document.getElementById('init-image');
    
    uploadAreaEl.onclick = () => fileInput.click();
    
    fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                document.getElementById('init-preview').src = event.target.result;
                document.getElementById('init-preview').style.display = 'block';
                document.getElementById('clear-image-btn').style.display = 'block';
                window.initImageData = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    };
    
    // Drag and drop
    uploadAreaEl.ondragover = (e) => {
        e.preventDefault();
        uploadAreaEl.style.borderColor = '#4CAF50';
    };
    
    uploadAreaEl.ondragleave = () => {
        uploadAreaEl.style.borderColor = '#444';
    };
    
    uploadAreaEl.ondrop = (e) => {
        e.preventDefault();
        uploadAreaEl.style.borderColor = '#444';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    };
    
    document.getElementById('denoising').oninput = (e) => {
        document.getElementById('denoising-value').textContent = e.target.value;
    };
}

function clearInitImage() {
    document.getElementById('init-preview').style.display = 'none';
    document.getElementById('clear-image-btn').style.display = 'none';
    document.getElementById('init-image').value = '';
    window.initImageData = null;
}

// Call this after DOM loads
document.addEventListener('DOMContentLoaded', setupImageUpload);
