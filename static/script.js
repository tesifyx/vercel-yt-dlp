
document.addEventListener('DOMContentLoaded', function() {
    const testForm = document.getElementById('testForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const responseCard = document.getElementById('responseCard');
    const responseContent = document.getElementById('responseContent');
    const actionSelect = document.getElementById('action');
    const qualityGroup = document.getElementById('qualityGroup');
    const audioOnlyCheckbox = document.getElementById('audioOnly');
    const videoUrlInput = document.getElementById('videoUrl');
    const useExampleUrlBtn = document.getElementById('useExampleUrl');
    const copyResponseBtn = document.getElementById('copyResponse');
    
    // Quick test buttons
    const testVideoInfoBtn = document.getElementById('testVideoInfo');
    const testDownloadLinkBtn = document.getElementById('testDownloadLink');
    const testPreviewLinkBtn = document.getElementById('testPreviewLink');
    
    // Response time tracking
    let requestStartTime = 0;

    // Example URL
    const exampleUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';

    // Use example URL
    useExampleUrlBtn.addEventListener('click', function() {
        videoUrlInput.value = exampleUrl;
        videoUrlInput.focus();
    });

    // Quick test buttons
    testVideoInfoBtn.addEventListener('click', function() {
        videoUrlInput.value = exampleUrl;
        actionSelect.value = 'info';
        audioOnlyCheckbox.checked = false;
        testForm.dispatchEvent(new Event('submit'));
    });

    testDownloadLinkBtn.addEventListener('click', function() {
        videoUrlInput.value = exampleUrl;
        actionSelect.value = 'download-link';
        document.getElementById('quality').value = '720p';
        audioOnlyCheckbox.checked = false;
        testForm.dispatchEvent(new Event('submit'));
    });

    testPreviewLinkBtn.addEventListener('click', function() {
        videoUrlInput.value = exampleUrl;
        actionSelect.value = 'preview-link';
        testForm.dispatchEvent(new Event('submit'));
    });

    // Handle action change
    actionSelect.addEventListener('change', function() {
        if (this.value === 'info' || this.value === 'preview-link') {
            qualityGroup.style.display = 'none';
            audioOnlyCheckbox.checked = false;
        } else {
            qualityGroup.style.display = 'block';
        }
    });

    // Handle audio-only checkbox
    audioOnlyCheckbox.addEventListener('change', function() {
        const qualitySelect = document.getElementById('quality');
        if (this.checked) {
            qualitySelect.innerHTML = `
                <option value="128kbps">128kbps</option>
                <option value="192kbps">192kbps</option>
                <option value="256kbps">256kbps</option>
                <option value="320kbps">320kbps</option>
            `;
        } else {
            qualitySelect.innerHTML = `
                <option value="720p">720p (HD)</option>
                <option value="1080p">1080p (Full HD)</option>
                <option value="480p">480p</option>
                <option value="360p">360p</option>
                <option value="240p">240p</option>
                <option value="144p">144p</option>
            `;
        }
    });

    // Copy response functionality
    copyResponseBtn.addEventListener('click', async function() {
        try {
            const responseText = responseContent.textContent;
            await navigator.clipboard.writeText(responseText);
            
            // Show feedback
            const originalText = copyResponseBtn.innerHTML;
            copyResponseBtn.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
            copyResponseBtn.classList.add('btn-success');
            copyResponseBtn.classList.remove('btn-outline-secondary');
            
            setTimeout(() => {
                copyResponseBtn.innerHTML = originalText;
                copyResponseBtn.classList.remove('btn-success');
                copyResponseBtn.classList.add('btn-outline-secondary');
            }, 2000);
        } catch (err) {
            console.log('Failed to copy: ', err);
            
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = responseContent.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    });

    // Handle form submission
    testForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = videoUrlInput.value.trim();
        const action = actionSelect.value;
        const quality = document.getElementById('quality').value;
        const audioOnly = audioOnlyCheckbox.checked;
        
        if (!url) {
            alert('Please enter a YouTube URL');
            return;
        }

        // Show loading
        loadingSpinner.classList.remove('d-none');
        responseCard.style.display = 'none';
        
        // Track request time
        requestStartTime = Date.now();
        
        try {
            let apiUrl;
            const params = new URLSearchParams({ url });
            
            if (action === 'info') {
                apiUrl = '/api/video-info';
            } else if (action === 'download-link') {
                apiUrl = '/api/download-link';
                params.append('quality', quality);
                if (audioOnly) params.append('audio_only', 'true');
            } else if (action === 'preview-link') {
                apiUrl = '/api/create-preview-link';
            }
            
            const response = await fetch(`${apiUrl}?${params}`);
            const data = await response.json();
            
            // Calculate response time
            const responseTime = Date.now() - requestStartTime;
            document.getElementById('responseTime').textContent = responseTime;
            document.getElementById('lastTest').textContent = new Date().toLocaleTimeString();
            
            // Display response
            displayResponse(data, response.status);
            
            // If it's a preview link, offer to open it
            if (action === 'preview-link' && data.success) {
                const openPreview = confirm('Preview link created! Would you like to open it in a new tab?');
                if (openPreview) {
                    window.open(data.preview_url, '_blank');
                }
            }
            
        } catch (error) {
            const responseTime = Date.now() - requestStartTime;
            document.getElementById('responseTime').textContent = responseTime;
            
            displayResponse({
                success: false,
                error: `Request failed: ${error.message}`
            }, 500);
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    });

    function displayResponse(data, status) {
        // Format JSON with syntax highlighting
        const formattedJson = JSON.stringify(data, null, 2);
        
        // Add status indicator
        const statusClass = status < 400 ? 'text-success' : 'text-danger';
        const statusIcon = status < 400 ? 'check-circle' : 'exclamation-triangle';
        
        responseContent.innerHTML = `
            <div class="mb-2">
                <span class="badge bg-secondary">HTTP ${status}</span>
                <i class="fas fa-${statusIcon} ${statusClass} ms-2"></i>
            </div>
            <pre class="json-syntax">${escapeHtml(formattedJson)}</pre>
        `;
        
        responseCard.style.display = 'block';
        responseCard.scrollIntoView({ behavior: 'smooth' });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize
    actionSelect.dispatchEvent(new Event('change'));
});
