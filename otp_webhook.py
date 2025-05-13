from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

app = FastAPI()

# ✅ Root route so you avoid 404
@app.get("/")
def root():
    return {"message": "FastAPI server is online!"}

otp_store: Dict[str, Dict] = {}  # sender_name → { message, timestamp }

class SmsMessage(BaseModel):
    sender: str  # This will be VFS
    message: str
    timestamp: str

@app.post("/sms-webhook")
async def receive_sms(sms: SmsMessage):
    print(f"📨 SMS received from {sms.sender}: {sms.message}")
    otp_store[sms.sender] = {
        "message": sms.message,
        "timestamp": sms.timestamp
    }
    return {"status": "received"}

@app.get("/otp/{sender}")
async def get_latest_otp(sender: str):
    return otp_store.get(sender, {"message": None, "timestamp": None})
