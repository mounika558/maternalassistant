// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
});

// Utility function to show loading state
function setLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');
    
    if (isLoading) {
        button.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'inline';
    } else {
        button.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
}

// Display risk level with appropriate styling
function displayRiskLevel(risk, probability, riskElementId, probabilityElementId) {
    const riskElement = document.getElementById(riskElementId);
    const probabilityElement = document.getElementById(probabilityElementId);
    
    let riskClass = 'risk-low';
    let riskText = 'Low Risk';
    
    if (probability >= 0.7) {
        riskClass = 'risk-high';
        riskText = 'High Risk';
    } else if (probability >= 0.4) {
        riskClass = 'risk-medium';
        riskText = 'Medium Risk';
    }
    
    riskElement.className = `risk-indicator ${riskClass}`;
    riskElement.textContent = `Risk Level: ${riskText}`;
    probabilityElement.textContent = `Risk Probability: ${(probability * 100).toFixed(1)}%`;
}

// Display recommendations
function displayRecommendations(recommendations, elementId) {
    const element = document.getElementById(elementId);
    
    let html = '<h4>Recommendations:</h4><ol>';
    recommendations.forEach(rec => {
        html += `<li>${rec}</li>`;
    });
    html += '</ol>';
    
    element.innerHTML = html;
}

// Display SHAP explanation
function displayShapExplanation(shapData, elementId) {
    const element = document.getElementById(elementId);
    
    if (!shapData || shapData.length === 0) {
        element.style.display = 'none';
        return;
    }
    
    let html = '<h4>Feature Importance (SHAP Values):</h4>';
    html += '<div class="shap-values">';
    
    shapData.forEach(item => {
        const percentage = (Math.abs(item.value) * 100).toFixed(1);
        const color = item.value > 0 ? '#f44336' : '#4caf50';
        
        html += `
            <div class="shap-item" style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <span>${item.feature}</span>
                    <span style="color: ${color}; font-weight: bold;">${percentage}%</span>
                </div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 5px;">
                    <div style="width: ${percentage}%; height: 100%; background: ${color}; border-radius: 4px;"></div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    element.innerHTML = html;
}

// Show error message
function showError(message) {
    alert(`Error: ${message}`);
}

// Calculate BMI
function calculateBMI(weight, height) {
    // height in cm, convert to meters
    const heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
}

// Validate form inputs
function validateFormInputs(formData) {
    for (let key in formData) {
        if (formData[key] === '' || formData[key] === null || formData[key] === undefined) {
            return false;
        }
    }
    return true;
}