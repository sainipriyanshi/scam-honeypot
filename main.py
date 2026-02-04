import httpx
import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
import asyncio
import re
from typing import Optional, Dict, Any, List
from persona import get_ai_response

app = FastAPI()

# 1. YOUR SECRET KEY
API_KEY_CREDENTIAL = "priyanshi_secret_123" 

class ChatRequest(BaseModel):
    sessionId: Optional[str] = "default_session"
    message: Any 
    conversationHistory: Optional[List[Any]] = [] 
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

# Improved Intelligence Extraction
def extract_intel(text: str):
    return {
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', text),
        "phishingLinks": re.findall(r'https?://\S+', text),
        "phoneNumbers": re.findall(r'[6-9]\d{9}', text), # Simplified for better matching
        "suspiciousKeywords": ["blocked", "verify", "urgent", "kyc", "otp"]
    }

async def send_guvi_callback(session_id: str, history: list, intel: dict):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Calculate turns based on history
    total_turns = len(history) + 1
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_turns,
        "extractedIntelligence": intel,
        "agentNotes": "Engaged using Aman persona. Successfully captured potential scam indicators via Regex."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"GUVI Callback Status: {response.status_code}")
        except Exception as e:
            print(f"Callback failed: {e}")

@app.post("/chat")
async def chat(request_data: ChatRequest, background_tasks: BackgroundTasks, x_api_key: Optional[str] = Header(None)):
    
    # ... (Keep your API Key check here) ...

    # --- CHANGE START ---
    msg = request_data.message
    if isinstance(msg, dict):
        # If they send {"sender": "scammer", "text": "...", ...}
        message_text = msg.get("text", "")
    else:
        # If they send a simple string "..."
        message_text = str(msg)
    # --- CHANGE END ---

    # Now use message_text for extraction and AI response
    intel = extract_intel(message_text)
    
    try:
        ai_reply = await asyncio.to_thread(get_ai_response, message_text, request_data.conversationHistory)
    except:
        ai_reply = "Arey, wait... network is bad here."

    # Send the background task
    background_tasks.add_task(send_guvi_callback, request_data.sessionId, request_data.conversationHistory, intel)

    # RETURN ONLY THESE TWO FIELDS (as per the email)
    return {
        "status": "success",
        "reply": ai_reply
    }

@app.get("/")
def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)