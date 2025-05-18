from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

@app.get("/")
def root():
    return {"message": "✅ FastAPI server is online!"}

otp_store: Dict[str, Dict] = {}  # sender_name → { message, timestamp }

class SmsMessage(BaseModel):
    sender: str  # Ex: 'VFS' or '+905312345678'
    message: str
    timestamp: str

def normalize_sender(sender: str) -> str:
    sender = sender.strip().replace(" ", "").replace("-", "")
    if sender.startswith("90") and not sender.startswith("+"):
        sender = "+" + sender
    return sender

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
    normalized_sender = normalize_sender(sender)
    return otp_store.get(normalized_sender, {"message": None, "timestamp": None})
