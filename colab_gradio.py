# === COPY AND PASTE THIS ENTIRE SCRIPT INTO A GOOGLE COLAB CELL ===
# First, run a separate cell with: !pip install gradio shap scikit-learn pandas matplotlib

import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt
import gradio as gr
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# ---------------------------------------------------------
# 1. TRAIN MODEL (Fast Synthetic Data)
# ---------------------------------------------------------
print("Generating Data and Training Model...")
np.random.seed(42)
N = 3000
wind_speed = np.random.normal(8, 3, N)              
wind_gust = wind_speed + np.random.normal(2, 1, N)
temperature = np.random.normal(15, 10, N)           
pressure = np.random.normal(1013, 8, N)             
humidity = np.random.uniform(30, 95, N)             
upper_wind_speed = wind_speed + np.random.normal(5, 2, N)
wind_shear = np.abs(upper_wind_speed - wind_speed)
temp_gradient = np.random.normal(6, 3, N)
instability_index = (temp_gradient * 0.3 + wind_shear * 0.4)

logit = (0.6 * wind_shear + 0.4 * wind_gust + 0.3 * temp_gradient - 0.002 * pressure + 0.01 * humidity - 5)
probability = 1 / (1 + np.exp(-logit))
turbulence = (np.random.rand(N) < probability).astype(int)

df = pd.DataFrame({
    "wind_speed": wind_speed, "wind_gust": wind_gust, "temperature": temperature,
    "pressure": pressure, "humidity": humidity, "upper_wind_speed": upper_wind_speed,
    "wind_shear": wind_shear, "temp_gradient": temp_gradient, 
    "instability_index": instability_index, "turbulence": turbulence
})

X = df.drop(columns=["turbulence"])
y = df["turbulence"]

model_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42))
])

model_pipeline.fit(X, y)

# Set up SHAP
classifier = model_pipeline.named_steps['classifier']
scaler = model_pipeline.named_steps['scaler']
explainer = shap.TreeExplainer(classifier)

print("Training Complete! Starting Interface...")

# ---------------------------------------------------------
# 2. GRADIO PREDICTION FUNCTION
# ---------------------------------------------------------
def predict_turbulence(wind_speed, wind_gust, temperature, pressure, humidity, upper_wind_speed, temp_gradient):
    # Calculate derived features
    wind_shear = abs(upper_wind_speed - wind_speed)
    instability_index = (temp_gradient * 0.3 + wind_shear * 0.4)
    
    # Needs to strictly match the X.columns layout
    input_data = pd.DataFrame([{
        "wind_speed": wind_speed, "wind_gust": wind_gust, "temperature": temperature,
        "pressure": pressure, "humidity": humidity, "upper_wind_speed": upper_wind_speed,
        "wind_shear": wind_shear, "temp_gradient": temp_gradient, "instability_index": instability_index
    }])
    
    # Predict
    pred = model_pipeline.predict(input_data)[0]
    prob = model_pipeline.predict_proba(input_data)[0][1]
    
    risk_msg = "🔥 HIGH RISK OF TURBULENCE 🔥" if pred == 1 else "✅ LOW RISK (Clear Skies)"
    prob_msg = f"{prob * 100:.1f} % Probability"
    
    # SHAP Explainability Plot
    input_scaled = scaler.transform(input_data)
    shap_values = explainer.shap_values(input_scaled)
    
    # Handle SHAP output structures
    if isinstance(shap_values, list):
        shap_to_plot = shap_values[1]  # positive class
    elif len(shap_values.shape) == 3:
        shap_to_plot = shap_values[:, :, 1]
    else:
        shap_to_plot = shap_values

    # Create the visual plot
    # Safely handle single/multi-output expected values to get a flat scalar scalar
    expected = explainer.expected_value
    base_val = float(expected[1][0] if isinstance(expected, list) and hasattr(expected[1], '__len__') else (expected[1] if isinstance(expected, list) else expected))

    fig = plt.figure(figsize=(10, 5))
    shap.waterfall_plot(shap.Explanation(
        values=shap_to_plot[0], 
        base_values=base_val, 
        data=input_data.iloc[0], 
        feature_names=input_data.columns.tolist()
    ), show=False)
    plt.tight_layout()
    
    return risk_msg, prob_msg, fig

# ---------------------------------------------------------
# 3. GRADIO INTERFACE
# ---------------------------------------------------------
theme = gr.themes.Soft(primary_hue="blue", neutral_hue="slate")

interface = gr.Interface(
    fn=predict_turbulence,
    inputs=[
        gr.Slider(0, 30, value=8.0, label="Wind Speed (m/s)"),
        gr.Slider(0, 40, value=10.0, label="Wind Gust (m/s)"),
        gr.Slider(-40, 40, value=15.0, label="Temperature (°C)"),
        gr.Slider(900, 1050, value=1013.0, label="Pressure (hPa)"),
        gr.Slider(0, 100, value=60.0, label="Humidity (%)"),
        gr.Slider(0, 50, value=13.0, label="Upper Wind Speed (m/s)"),
        gr.Slider(-10, 10, value=6.0, label="Temperature Gradient"),
    ],
    outputs=[
        gr.Textbox(label="Risk Assessment", text_color="red"),
        gr.Textbox(label="Probability Score"),
        gr.Plot(label="SHAP Feature Explainer (Why did it predict this?)")
    ],
    title="✈️ Turbulence Predictor (AI powered by SHAP)",
    description="Adjust the flight parameters below to see the risk of turbulence. The chart shows exactly which weather features contributed to the decision.",
    theme=theme
)

# Launch with share=True to create the public URL
interface.launch(share=True, debug=True)
