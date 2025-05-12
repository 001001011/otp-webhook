from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# ✅ Root route so you avoid 404
@app.get("/")
def root():
    return {"message": "FastAPI server is online!"}

# In-memory storage for latest OTPs
otp_storage = {}

class SmsMessage(BaseModel):
    sender: str
    message: str
    timestamp: str = None

@app.post("/sms-webhook")
async def receive_sms(msg: SmsMessage):
    otp_storage[msg.sender] = {
        "message": msg.message,
        "timestamp": msg.timestamp or datetime.utcnow().isoformat()
    }
    print(f"📨 SMS received from {msg.sender}: {msg.message}")
    return {"status": "received"}

@app.get("/otp/{sender}")
def get_latest_otp(sender: str):
    if sender in otp_storage:
        return otp_storage[sender]
    return {"error": "No OTP found for this sender"}
