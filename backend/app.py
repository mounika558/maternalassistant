from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
from werkzeug.utils import secure_filename

# Import utility modules
from utils.signal_processor import process_signal_file
from utils.feature_extractor import extract_ehg_features, extract_ctg_features
from utils.explainer import get_shap_explanation

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'dat'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load models at startup
print("Loading models...")
try:
    # EHG/Preterm models
    with open('models/ehg_scaler.pkl', 'rb') as f:
        ehg_scaler = pickle.load(f)
    with open('models/ehg_rf_model.pkl', 'rb') as f:
        ehg_model = pickle.load(f)
    
    # CTG/Acidemia models
    with open('models/scaler.pkl', 'rb') as f:
        ctg_scaler = pickle.load(f)
    with open('models/random_forest_tuned.pkl', 'rb') as f:
        ctg_model = pickle.load(f)
    
    print("All models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_recommendations(prediction_type, risk_probability):
    """Generate recommendations based on prediction type and risk level"""
    
    if prediction_type == 'preterm':
        if risk_probability < 0.3:
            return [
                "Continue regular prenatal care visits",
                "Monitor for any changes in symptoms",
                "Maintain a healthy, balanced diet",
                "Get adequate rest and avoid stress",
                "Follow standard pregnancy guidelines"
            ]
        elif risk_probability < 0.7:
            return [
                "Increase frequency of prenatal visits",
                "Monitor for signs of preterm labor (contractions, back pain, pressure)",
                "Consider cervical length monitoring via ultrasound",
                "Discuss progesterone supplementation with your doctor",
                "Avoid strenuous activities and heavy lifting",
                "Stay hydrated and maintain healthy nutrition"
            ]
        else:
            return [
                "URGENT: Schedule immediate consultation with maternal-fetal medicine specialist",
                "Frequent monitoring and possible bed rest may be recommended",
                "Discuss corticosteroids for fetal lung maturation",
                "Learn signs of preterm labor and when to seek emergency care",
                "Consider hospitalization for close monitoring if recommended",
                "Prepare birth plan for potential preterm delivery"
            ]
    
    elif prediction_type == 'acidemia':
        if risk_probability < 0.3:
            return [
                "Continue routine fetal monitoring during prenatal visits",
                "Maintain healthy lifestyle and nutrition",
                "Report any decreased fetal movement immediately",
                "Follow standard labor and delivery protocols",
                "No additional interventions needed at this time"
            ]
        elif risk_probability < 0.7:
            return [
                "Increase frequency of fetal heart rate monitoring",
                "Consider non-stress tests (NST) more frequently",
                "Monitor for signs of fetal distress during labor",
                "Discuss delivery timing with your obstetrician",
                "Be prepared for possible intervention during labor"
            ]
        else:
            return [
                "URGENT: Immediate continuous fetal monitoring required",
                "Discuss delivery options with your medical team urgently",
                "May require cesarean section or assisted delivery",
                "Prepare for potential NICU admission after birth",
                "Close monitoring during labor is essential",
                "Consider early delivery if near term"
            ]
    
    return []

@app.route('/api/predict/preterm', methods=['POST'])
def predict_preterm_signal():
    """Predict preterm birth from EHG signal file"""
    
    if 'signal_file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['signal_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .dat files are allowed'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process signal file
        signal_data = process_signal_file(filepath)
        
        # Extract features
        features = extract_ehg_features(signal_data)
        
        # Scale features
        features_scaled = ehg_scaler.transform([features])
        
        # Make prediction
        prediction = ehg_model.predict(features_scaled)[0]
        probability = ehg_model.predict_proba(features_scaled)[0][1]
        
        # Get SHAP explanation
        shap_values = get_shap_explanation(ehg_model, features_scaled, 
                                          feature_names=['Feature ' + str(i) for i in range(len(features))])
        
        # Get recommendations
        recommendations = get_recommendations('preterm', probability)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'recommendations': recommendations,
            'shap_values': shap_values
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/acidemia', methods=['POST'])
def predict_acidemia_signal():
    """Predict fetal acidemia from CTG signal file"""
    
    if 'signal_file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['signal_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .dat files are allowed'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process signal file
        signal_data = process_signal_file(filepath)
        
        # Extract features
        features = extract_ctg_features(signal_data)
        
        # Scale features
        features_scaled = ctg_scaler.transform([features])
        
        # Make prediction
        prediction = ctg_model.predict(features_scaled)[0]
        probability = ctg_model.predict_proba(features_scaled)[0][1]
        
        # Get SHAP explanation
        shap_values = get_shap_explanation(ctg_model, features_scaled,
                                          feature_names=['Feature ' + str(i) for i in range(len(features))])
        
        # Get recommendations
        recommendations = get_recommendations('acidemia', probability)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'recommendations': recommendations,
            'shap_values': shap_values
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/preterm-form', methods=['POST'])
def predict_preterm_form():
    """Predict preterm birth from patient form data"""
    
    try:
        data = request.get_json()
        
        # Extract features from form data
        # Note: Adjust these based on your actual model's expected features
        features = [
            data['maternal_age'],
            data['gestational_age'],
            data['systolic_bp'],
            data['diastolic_bp'],
            data['weight'],
            data['height'],
            data['bmi'],
            data['previous_pregnancies'],
            data['diabetes']
        ]
        
        # Scale features
        features_scaled = ehg_scaler.transform([features])
        
        # Make prediction
        prediction = ehg_model.predict(features_scaled)[0]
        probability = ehg_model.predict_proba(features_scaled)[0][1]
        
        # Get recommendations
        recommendations = get_recommendations('preterm', probability)
        
        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/acidemia-form', methods=['POST'])
def predict_acidemia_form():
    """Predict fetal acidemia from patient form data"""
    
    try:
        data = request.get_json()
        
        # Extract features from form data
        features = [
            data['maternal_age'],
            data['gestational_age'],
            data['systolic_bp'],
            data['diastolic_bp'],
            data['weight'],
            data['height'],
            data['bmi'],
            data['previous_pregnancies'],
            data['diabetes']
        ]
        
        # Scale features
        features_scaled = ctg_scaler.transform([features])
        
        # Make prediction
        prediction = ctg_model.predict(features_scaled)[0]
        probability = ctg_model.predict_proba(features_scaled)[0][1]
        
        # Get recommendations
        recommendations = get_recommendations('acidemia', probability)
        
        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)