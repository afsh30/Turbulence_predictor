from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import shap

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = None
MODEL_PATH = "backend/model/turbulence_model.joblib"
explainer = None

@app.on_event("startup")
def load_model():
    global model, explainer
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully.")
            
            classifier = model.named_steps['classifier']
            explainer = shap.TreeExplainer(classifier)
            print("SHAP Explainer initialized.")
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}. Make sure to run train.py first.")

class TurbulenceInput(BaseModel):
    wind_speed: float
    wind_gust: float
    temperature: float
    pressure: float
    humidity: float
    upper_wind_speed: float
    temp_gradient: float

@app.post("/predict")
def predict_turbulence(data: TurbulenceInput):
    if model is None:
        return {"error": "Model not loaded properly. Please train the model first."}
    
    wind_shear = abs(data.upper_wind_speed - data.wind_speed)
    instability_index = (data.temp_gradient * 0.3 + wind_shear * 0.4)
    
    features = {
        "wind_speed": data.wind_speed,
        "wind_gust": data.wind_gust,
        "temperature": data.temperature,
        "pressure": data.pressure,
        "humidity": data.humidity,
        "upper_wind_speed": data.upper_wind_speed,
        "wind_shear": wind_shear,
        "temp_gradient": data.temp_gradient,
        "instability_index": instability_index
    }
    
    input_df = pd.DataFrame([features])
    
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]
    
    scaler = model.named_steps['scaler']
    input_scaled = scaler.transform(input_df)
    
    shap_values = explainer.shap_values(input_scaled)
    
    # Robustly handle SHAP output format
    if isinstance(shap_values, list):
        shap_contributions = shap_values[1][0]
    elif len(shap_values.shape) == 3:
        shap_contributions = shap_values[0, :, 1]
    else:
        shap_contributions = shap_values[0]

    feature_names = input_df.columns
    contributions = dict(zip(feature_names, shap_contributions))
    
    sorted_contributions = sorted(
        contributions.items(), 
        key=lambda x: abs(x[1]), 
        reverse=True
    )
    
    explanation = [
        {"feature": k, "contribution": float(v)} 
        for k, v in sorted_contributions
    ]
    
    return {
        "turbulence_risk": int(prediction),
        "risk_probability": float(probability),
        "message": "High Turbulence Risk" if prediction == 1 else "Low Turbulence Risk",
        "explanation": explanation
    }

@app.get("/")
def read_root():
    return {"message": "Turbulence Prediction API is running"}
