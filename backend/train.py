import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score

# Create model directory if not exists
os.makedirs('backend/model', exist_ok=True)

np.random.seed(42)

def train_model():
    print("Generating synthetic data...")
    # ===================================
    # 1. Generate Synthetic Weather Data
    # ===================================

    N = 3000

    wind_speed = np.random.normal(8, 3, N)              # m/s
    wind_gust = wind_speed + np.random.normal(2, 1, N)
    temperature = np.random.normal(15, 10, N)           # °C
    pressure = np.random.normal(1013, 8, N)             # hPa
    humidity = np.random.uniform(30, 95, N)             # %
    upper_wind_speed = wind_speed + np.random.normal(5, 2, N)
    wind_shear = np.abs(upper_wind_speed - wind_speed)
    temp_gradient = np.random.normal(6, 3, N)
    instability_index = (temp_gradient * 0.3 + wind_shear * 0.4)

    # ===================================
    # 2. Define Turbulence Probability
    # ===================================

    logit = (
        0.6 * wind_shear +
        0.4 * wind_gust +
        0.3 * temp_gradient -
        0.002 * pressure +
        0.01 * humidity -
        5
    )

    probability = 1 / (1 + np.exp(-logit))

    turbulence = (np.random.rand(N) < probability).astype(int)

    # ===================================
    # 3. Create DataFrame
    # ===================================

    df = pd.DataFrame({
        "wind_speed": wind_speed,
        "wind_gust": wind_gust,
        "temperature": temperature,
        "pressure": pressure,
        "humidity": humidity,
        "upper_wind_speed": upper_wind_speed,
        "wind_shear": wind_shear,
        "temp_gradient": temp_gradient,
        "instability_index": instability_index,
        "turbulence": turbulence
    })

    print("Turbulence rate:", df["turbulence"].mean())

    # ===================================
    # 4. Train/Test Split
    # ===================================

    X = df.drop(columns=["turbulence"])
    y = df["turbulence"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # ===================================
    # 5. Build Model Pipeline
    # ===================================

    model_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42
        ))
    ])

    print("Training model...")
    model_pipeline.fit(X_train, y_train)

    # ===================================
    # 6. Evaluation
    # ===================================

    y_pred = model_pipeline.predict(X_test)
    y_prob = model_pipeline.predict_proba(X_test)[:, 1]

    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))
    print("ROC AUC:", roc_auc_score(y_test, y_prob))

    # ===================================
    # 7. SHAP Explainability
    # ===================================
    print("\nGenerating SHAP summary...")
    # For Pipeline, we need to bypass the scaler for the explainer or transform the data
    # It is easier to explain the classifier using transformed data
    
    # Transform test data using the scaler
    scaler = model_pipeline.named_steps['scaler']
    classifier = model_pipeline.named_steps['classifier']
    X_test_scaled = scaler.transform(X_test)
    X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X.columns)

    # Create explainer
    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(X_test_scaled_df)

    # Save summary plot
    plt.figure()
    # For binary classification, shap_values is a list of length 2.
    # We want index 1 (positive class). 
    # If it's already an array (newer shap versions sometimes return array for binary), handle that.
    if isinstance(shap_values, list):
        vals_to_plot = shap_values[1]
    else:
        # If it's an array (N, M, 2) or just (N, M)
        if len(shap_values.shape) == 3:
            vals_to_plot = shap_values[:, :, 1]
        else:
            vals_to_plot = shap_values

    shap.summary_plot(vals_to_plot, X_test_scaled_df, show=False)
    plt.savefig('backend/model/shap_summary.png', bbox_inches='tight')
    plt.close()
    print("SHAP summary plot saved to backend/model/shap_summary.png")

    # ===================================
    # 8. Save Model
    # ===================================

    joblib.dump(model_pipeline, "backend/model/turbulence_model.joblib")
    print("\nModel saved to backend/model/turbulence_model.joblib")

if __name__ == "__main__":
    train_model()
