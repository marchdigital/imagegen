document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const generateButton = document.querySelector('button[type=submit]');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                prompt document.querySelector('input[type=text], textarea').value,
                aspect_ratio document.querySelector('select').value  '11',
                output_format 'webp',
                quality 80
            };
            
            console.log('Submitting', formData);
            
            try {
                generateButton.disabled = true;
                generateButton.textContent = 'Generating...';
                
                const response = await fetch('apiextendedwan25', {
                    method 'POST',
                    body new FormData(form)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status ${response.status}`);
                }
                
                const result = await response.json();
                console.log('Result', result);
                
                 Display the result
                if (result.result && result.result.images) {
                    const container = document.querySelector('.image-container')  document.body;
                    result.result.images.forEach(img = {
                        const imgEl = document.createElement('img');
                        imgEl.src = img.url  `dataimagepng;base64,${img.data}`;
                        imgEl.style.maxWidth = '100%';
                        container.appendChild(imgEl);
                    });
                }
            } catch (error) {
                console.error('Generation failed', error);
                alert('Generation failed ' + error.message);
            } finally {
                generateButton.disabled = false;
                generateButton.textContent = 'Generate with WAN-25';
            }
        });
    }
});