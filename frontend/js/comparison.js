function openComparisonView(images) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.9);
        z-index: 2000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: #242424;
        padding: 30px;
        border-radius: 8px;
        max-width: 90vw;
        max-height: 90vh;
        overflow: auto;
    `;
    
    content.innerHTML = `
        <h2>⚖️ Image Comparison</h2>
        <div style="display: grid; grid-template-columns: repeat(${Math.min(images.length, 3)}, 1fr); gap: 20px; margin-top: 20px;">
            ${images.map((img, i) => `
                <div>
                    <img src="${img.url}" style="width: 100%; border-radius: 4px;">
                    <div style="background: #1a1a1a; padding: 10px; margin-top: 10px; border-radius: 4px; font-size: 12px;">
                        <p>Model: ${img.model}</p>
                        <p>Size: ${img.width}x${img.height}</p>
                        <p>CFG: ${img.cfg_scale}</p>
                        <p>Steps: ${img.steps}</p>
                    </div>
                    <button class="btn" onclick="selectWinner(${img.id})" style="width: 100%; margin-top: 10px;">
                        Select as Best
                    </button>
                </div>
            `).join('')}
        </div>
        <button onclick="this.parentElement.parentElement.remove()" style="margin-top: 20px; padding: 10px 20px; background: #555; color: white; border: none; border-radius: 4px;">
            Close
        </button>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
}

function selectWinner(imageId) {
    console.log('Selected winner:', imageId);
    // Mark as favorite or preferred
    fetch(`/api/gallery/${imageId}/favorite`, { method: 'POST' });
}
