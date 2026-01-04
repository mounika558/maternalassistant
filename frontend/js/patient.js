// Patient Portal - Form-based Risk Assessment

// Preterm Form Submission
document.getElementById('preterm-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        maternal_age: parseFloat(document.getElementById('maternal-age').value),
        gestational_age: parseFloat(document.getElementById('gestational-age').value),
        systolic_bp: parseFloat(document.getElementById('systolic-bp').value),
        diastolic_bp: parseFloat(document.getElementById('diastolic-bp').value),
        weight: parseFloat(document.getElementById('weight').value),
        height: parseFloat(document.getElementById('height').value),
        previous_pregnancies: parseInt(document.getElementById('previous-pregnancies').value),
        diabetes: document.getElementById('diabetes').value === 'yes' ? 1 : 0
    };
    
    // Calculate BMI
    formData.bmi = calculateBMI(formData.weight, formData.height);
    
    if (!validateFormInputs(formData)) {
        showError('Please fill in all required fields');
        return;
    }
    
    setLoading('preterm-form', true);
    const submitBtn = document.querySelector('#preterm-form button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    btnText.style.display = 'none';
    loader.style.display = 'inline';
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/preterm-form`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Prediction failed');
        }
        
        const result = await response.json();
        
        // Display results
        displayRiskLevel(result.prediction, result.probability, 'preterm-risk-level', 'preterm-probability');
        displayRecommendations(result.recommendations, 'preterm-recommendations');
        
        document.getElementById('preterm-results').style.display = 'block';
        
        // Scroll to results
        document.getElementById('preterm-results').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        showError('Failed to analyze risk: ' + error.message);
    } finally {
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
});

// Acidemia Form Submission
document.getElementById('acidemia-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        maternal_age: parseFloat(document.getElementById('maternal-age-acid').value),
        gestational_age: parseFloat(document.getElementById('gestational-age-acid').value),
        systolic_bp: parseFloat(document.getElementById('systolic-bp-acid').value),
        diastolic_bp: parseFloat(document.getElementById('diastolic-bp-acid').value),
        weight: parseFloat(document.getElementById('weight-acid').value),
        height: parseFloat(document.getElementById('height-acid').value),
        previous_pregnancies: parseInt(document.getElementById('previous-pregnancies-acid').value),
        diabetes: document.getElementById('diabetes-acid').value === 'yes' ? 1 : 0
    };
    
    // Calculate BMI
    formData.bmi = calculateBMI(formData.weight, formData.height);
    
    if (!validateFormInputs(formData)) {
        showError('Please fill in all required fields');
        return;
    }
    
    const submitBtn = document.querySelector('#acidemia-form button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    btnText.style.display = 'none';
    loader.style.display = 'inline';
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/acidemia-form`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Prediction failed');
        }
        
        const result = await response.json();
        
        // Display results
        displayRiskLevel(result.prediction, result.probability, 'acidemia-risk-level', 'acidemia-probability');
        displayRecommendations(result.recommendations, 'acidemia-recommendations');
        
        document.getElementById('acidemia-results').style.display = 'block';
        
        // Scroll to results
        document.getElementById('acidemia-results').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        showError('Failed to analyze risk: ' + error.message);
    } finally {
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
});

// Auto-calculate and display BMI as user types
function setupBMICalculator(weightId, heightId) {
    const weightInput = document.getElementById(weightId);
    const heightInput = document.getElementById(heightId);
    
    function updateBMI() {
        const weight = parseFloat(weightInput.value);
        const height = parseFloat(heightInput.value);
        
        if (weight && height) {
            const bmi = calculateBMI(weight, height);
            console.log(`BMI: ${bmi.toFixed(1)}`);
        }
    }
    
    weightInput.addEventListener('input', updateBMI);
    heightInput.addEventListener('input', updateBMI);
}

// Setup BMI calculators for both forms
setupBMICalculator('weight', 'height');
setupBMICalculator('weight-acid', 'height-acid');