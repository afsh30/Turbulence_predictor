# Turbulence Prediction Web App

## Prerequisites
- **Python 3.8+**
- **Node.js 16+**

## Setup & Running

### 1. Backend (Python)
Navigate to the `backend` folder and set up the environment:

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

Train the model:
```bash
python train.py
```

Run the API server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 2. Frontend (React)
Open a new terminal, navigate to the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```
The web app will run at `http://localhost:5173`.

## Features
- **Synthetic Data Generation**: Creates realistic flight data for training.
- **Random Forest Model**: Predicts turbulence risk based on wind shear, temperature gradient, humidity, and altitude.
- **FastAPI Backend**: Serves predictions via REST API.
- **Modern React UI**: beautiful glassmorphism design with real-time risk assessment.
