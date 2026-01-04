"""
SHAP Explainer - Provides interpretable explanations for model predictions
"""

import numpy as np
import shap

def get_shap_explanation(model, features, feature_names=None, max_features=5):
    """
    Generate SHAP values for model explanation
    
    Args:
        model: Trained ML model
        features: Feature array (scaled)
        feature_names: List of feature names (optional)
        max_features: Maximum number of top features to return
        
    Returns:
        List of dictionaries with feature importance
    """
    try:
        # Create SHAP explainer
        # For Random Forest, use TreeExplainer
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(features)
        
        # For binary classification, get values for positive class
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]
        
        # Get absolute values for ranking
        shap_values_abs = np.abs(shap_values[0])
        
        # Create feature names if not provided
        if feature_names is None:
            feature_names = [f'Feature_{i}' for i in range(len(shap_values_abs))]
        
        # Sort by importance
        indices = np.argsort(shap_values_abs)[::-1]
        
        # Create result list
        result = []
        for i in range(min(max_features, len(indices))):
            idx = indices[i]
            result.append({
                'feature': feature_names[idx],
                'value': float(shap_values[0][idx]),
                'abs_value': float(shap_values_abs[idx])
            })
        
        return result
        
    except Exception as e:
        print(f"Error generating SHAP explanation: {e}")
        # Return empty list if SHAP fails
        return []

def get_feature_importance_from_model(model, feature_names=None, max_features=5):
    """
    Get feature importance directly from Random Forest model
    (Fallback if SHAP fails)
    
    Args:
        model: Trained Random Forest model
        feature_names: List of feature names
        max_features: Maximum number of features to return
        
    Returns:
        List of dictionaries with feature importance
    """
    try:
        importances = model.feature_importances_
        
        if feature_names is None:
            feature_names = [f'Feature_{i}' for i in range(len(importances))]
        
        # Sort by importance
        indices = np.argsort(importances)[::-1]
        
        result = []
        for i in range(min(max_features, len(indices))):
            idx = indices[i]
            result.append({
                'feature': feature_names[idx],
                'value': float(importances[idx]),
                'abs_value': float(importances[idx])
            })
        
        return result
        
    except Exception as e:
        print(f"Error getting feature importance: {e}")
        return []

def explain_prediction(model, features, feature_names=None, use_shap=True):
    """
    Main function to explain a prediction
    
    Args:
        model: Trained model
        features: Feature array
        feature_names: List of feature names
        use_shap: Whether to use SHAP (True) or feature importance (False)
        
    Returns:
        Explanation dictionary
    """
    if use_shap:
        try:
            return get_shap_explanation(model, features, feature_names)
        except:
            # Fallback to feature importance
            return get_feature_importance_from_model(model, feature_names)
    else:
        return get_feature_importance_from_model(model, feature_names)