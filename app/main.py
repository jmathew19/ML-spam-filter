# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

# Load saved model and vectorizer
model = joblib.load("app/model.pkl")
vectorizer = joblib.load("app/vectorizer.pkl")

app = FastAPI()

# Define the input format
class Message(BaseModel):
    text: str

@app.post("/predict")
def predict(msg: Message):
    # Transform the input text
    X = vectorizer.transform([msg.text])
    # Get the prediction
    prediction = model.predict(X)[0]
    return {"prediction": prediction}
