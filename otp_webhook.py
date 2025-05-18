from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

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

    # Remove any "from", colons, and extra spacing
    if sender.startswith("from"):
        sender = sender.replace("from", "").replace(":", "").strip()

    # Normalize Turkish mobile format: 905xx… → +905xx…
    if sender.startswith("90") and not sender.startswith("+"):
        sender = "+" + sender

    return sender.upper()  # Use upper-case keys in store

@app.post("/sms-webhook")
async def receive_sms(sms: SmsMessage):
    sender_key = normalize_sender(sms.sender)

    otp_store[sender_key] = {
        "message": sms.message,
        "timestamp": sms.timestamp
    }

    print(f"📨 SMS received from {sender_key}: {sms.message}")
    print("🧾 Current keys in store:", list(otp_store.keys()))

    return {"status": "received"}

@app.get("/otp/{sender}")
async def get_latest_otp(sender: str):
    sender_key = normalize_sender(sender)
    return otp_store.get(sender_key, {"message": None, "timestamp": None})
