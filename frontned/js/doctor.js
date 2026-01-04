// Doctor Portal - Signal File Upload and Analysis

// EHG Signal Processing
document.getElementById('ehg-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('ehg-file-name').textContent = `Selected: ${file.name}`;
        document.getElementById('analyze-ehg').disabled = false;
    }
});

document.getElementById('analyze-ehg').addEventListener('click', async function() {
    const fileInput = document.getElementById('ehg-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a .dat file first');
        return;
    }
    
    setLoading('analyze-ehg', true);
    
    const formData = new FormData();
    formData.append('signal_file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/preterm`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Prediction failed');
        }
        
        const result = await response.json();
        
        // Display results
        displayRiskLevel(result.prediction, result.probability, 'ehg-risk-level', 'ehg-probability');
        displayRecommendations(result.recommendations, 'ehg-recommendations');
        
        if (result.shap_values) {
            displayShapExplanation(result.shap_values, 'ehg-shap');
        }
        
        document.getElementById('ehg-results').style.display = 'block';
        
    } catch (error) {
        showError('Failed to analyze EHG signal: ' + error.message);
    } finally {
        setLoading('analyze-ehg', false);
    }
});

// CTG Signal Processing
document.getElementById('ctg-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('ctg-file-name').textContent = `Selected: ${file.name}`;
        document.getElementById('analyze-ctg').disabled = false;
    }
});

document.getElementById('analyze-ctg').addEventListener('click', async function() {
    const fileInput = document.getElementById('ctg-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a .dat file first');
        return;
    }
    
    setLoading('analyze-ctg', true);
    
    const formData = new FormData();
    formData.append('signal_file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/acidemia`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Prediction failed');
        }
        
        const result = await response.json();
        
        // Display results
        displayRiskLevel(result.prediction, result.probability, 'ctg-risk-level', 'ctg-probability');
        displayRecommendations(result.recommendations, 'ctg-recommendations');
        
        if (result.shap_values) {
            displayShapExplanation(result.shap_values, 'ctg-shap');
        }
        
        document.getElementById('ctg-results').style.display = 'block';
        
    } catch (error) {
        showError('Failed to analyze CTG signal: ' + error.message);
    } finally {
        setLoading('analyze-ctg', false);
    }
});

// Drag and drop functionality for EHG
const ehgUploadArea = document.getElementById('ehg-upload-area');
ehgUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    ehgUploadArea.style.background = '#f0f0ff';
});

ehgUploadArea.addEventListener('dragleave', () => {
    ehgUploadArea.style.background = '';
});

ehgUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    ehgUploadArea.style.background = '';
    
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.dat')) {
        document.getElementById('ehg-file').files = e.dataTransfer.files;
        document.getElementById('ehg-file-name').textContent = `Selected: ${file.name}`;
        document.getElementById('analyze-ehg').disabled = false;
    } else {
        showError('Please drop a .dat file');
    }
});

// Drag and drop functionality for CTG
const ctgUploadArea = document.getElementById('ctg-upload-area');
ctgUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    ctgUploadArea.style.background = '#f0f0ff';
});

ctgUploadArea.addEventListener('dragleave', () => {
    ctgUploadArea.style.background = '';
});

ctgUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    ctgUploadArea.style.background = '';
    
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.dat')) {
        document.getElementById('ctg-file').files = e.dataTransfer.files;
        document.getElementById('ctg-file-name').textContent = `Selected: ${file.name}`;
        document.getElementById('analyze-ctg').disabled = false;
    } else {
        showError('Please drop a .dat file');
    }
});