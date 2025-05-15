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

@app.post("/sms-webhook")
async def receive_sms(sms: SmsMessage):
    sender_key = sms.sender.strip()

    otp_store[sender_key] = {
        "message": sms.message,
        "timestamp": sms.timestamp
    }

    print(f"📨 SMS received from {sender_key}: {sms.message}")
    print("🧾 Current keys in store:", list(otp_store.keys()))

    return {"status": "received"}

@app.get("/otp/{sender}")
async def get_latest_otp(sender: str):
    return otp_store.get(sender.strip(), {"message": None, "timestamp": None})
