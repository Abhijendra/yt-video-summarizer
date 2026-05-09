// Get DOM elements
const videoInput = document.getElementById('videoLink');
const generateBtn = document.getElementById('generateBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultSection = document.getElementById('resultSection');
const summaryTextarea = document.getElementById('summaryText');
const errorMessage = document.getElementById('errorMessage');

const API_BASE_URL = '';

// Event listeners
generateBtn.addEventListener('click', handleGenerate);
resetBtn.addEventListener('click', handleReset);
videoInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleGenerate();
    }
});

// Generate summary function
async function handleGenerate() {
    const videoLink = videoInput.value.trim();
    
    // Validate input
    if (!videoLink) {
        showError('Please paste a YouTube video link');
        return;
    }
    
    if (!isValidYouTubeUrl(videoLink)) {
        showError('Please enter a valid YouTube URL');
        return;
    }
    
    // Hide error and result, show loading
    hideError();
    hideResult();
    showLoading();
    
    // Disable button during request
    generateBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/fetch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain'
            },
            body: videoLink
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            summaryTextarea.value = data.generated_summary;
            showResult();
        } else {
            throw new Error('Failed to generate summary');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to fetch summary. Please try again.');
    } finally {
        hideLoading();
        generateBtn.disabled = false;
    }
}

// Reset function
function handleReset() {
    videoInput.value = '';
    summaryTextarea.value = '';
    hideResult();
    hideError();
    videoInput.focus();
}

// Validate YouTube URL
function isValidYouTubeUrl(url) {
    const patterns = [
        /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=)[a-zA-Z0-9_-]{11}/,
        /^(https?:\/\/)?(www\.)?(youtu\.be\/)[a-zA-Z0-9_-]{11}/,
        /^(https?:\/\/)?(www\.)?(youtube\.com\/embed\/)[a-zA-Z0-9_-]{11}/,
        /^(https?:\/\/)?(www\.)?(youtube\.com\/v\/)[a-zA-Z0-9_-]{11}/
    ];
    
    return patterns.some(pattern => pattern.test(url));
}

// UI helper functions
function showLoading() {
    loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
}

function showResult() {
    resultSection.classList.remove('hidden');
}

function hideResult() {
    resultSection.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}