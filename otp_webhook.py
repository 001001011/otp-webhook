from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import re

app = FastAPI()

@app.get("/")
def root():
    return {"message": "✅ FastAPI server is online!"}

# In-memory store: sender → { message, timestamp }
otp_store: Dict[str, Dict] = {}

class SmsMessage(BaseModel):
    sender: str  # Can be a phone number or service name
    message: str
    timestamp: str

def normalize_sender(sender: str) -> str:
    sender = sender.strip().lower()

    # Remove common leading patterns like "from:" or "FROM :"
    sender = re.sub(r"^from[:\s]*", "", sender, flags=re.IGNORECASE)

    # Normalize Turkish mobile format: 905xx… → +905xx…
    if sender.startswith("90") and not sender.startswith("+"):
        sender = "+" + sender

    return sender.upper()

def clean_text(text: str) -> str:
    # Remove leading/trailing whitespace, and collapse internal multiple spaces/newlines
    return re.sub(r"\s+", " ", text.strip())

@app.post("/sms-webhook")
async def receive_sms(sms: SmsMessage):
    sender_key = normalize_sender(sms.sender)
    cleaned_message = clean_text(sms.message)
    cleaned_timestamp = clean_text(sms.timestamp)

    otp_store[sender_key] = {
        "message": cleaned_message,
        "timestamp": cleaned_timestamp
    }

    print(f"📨 SMS received from {sender_key}: {cleaned_message}")
    print("🧾 Current keys in store:", list(otp_store.keys()))

    return {"status": "received"}

@app.get("/otp/{sender}")
async def get_latest_otp(sender: str):
    sender_key = normalize_sender(sender)
    return otp_store.get(sender_key, {"message": None, "timestamp": None})
