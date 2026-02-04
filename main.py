import httpx
import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
import asyncio
import re
from typing import Optional, Dict, Any, List
from persona import get_ai_response

app = FastAPI()

# 1. YOUR SECRET KEY (Now correctly set)
API_KEY_CREDENTIAL = "priyanshi_secret_123" 

class ChatRequest(BaseModel):
    sessionId: Optional[str] = "default_session"
    message: Any 
    conversationHistory: Optional[List[Dict[str, Any]]] = [] 
    metadata: Optional[Dict[str, Any]] = None

# Improved Intelligence Extraction
def extract_intel(text: str):
    return {
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', text),
        "phishingLinks": re.findall(r'https?://\S+', text),
        "phoneNumbers": re.findall(r'\b[6-9]\d{9}\b', text),
        "suspiciousKeywords": ["blocked", "verify", "urgent", "kyc", "otp"]
    }

async def send_guvi_callback(session_id: str, history: list, intel: dict):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    total_turns = len(history) + 2 
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_turns,
        "extractedIntelligence": intel,
        "agentNotes": "Engaged using Aman persona. Successfully captured potential scam indicators via Regex."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Added a print here so you can check your Render logs to see if GUVI accepted it
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"GUVI Callback Status: {response.status_code}")
        except Exception as e:
            print(f"Callback failed: {e}")

@app.post("/chat")
async def chat(
    request_data: ChatRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None) 
):
    # Security Check
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    session_id = request_data.sessionId
    
    if isinstance(request_data.message, dict):
        message_text = request_data.message.get("text", "")
    else:
        message_text = str(request_data.message)

    try:
        # AI Response logic using your persona.py
        ai_reply = await asyncio.wait_for(
            asyncio.to_thread(get_ai_response, message_text, request_data.conversationHistory),
            timeout=20.0
        )
    except Exception as e:
        print(f"Chat Route Error: {e}")
        ai_reply = "Wait, my phone is acting up. What did you say?"

    combined_text = message_text + " " + str(request_data.conversationHistory)
    intel = extract_intel(combined_text)
    
    # Trigger callback in the background
    background_tasks.add_task(send_guvi_callback, session_id, request_data.conversationHistory, intel)

    return {
        "status": "success",
        "reply": ai_reply
    }

@app.get("/")
def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    # This change ensures it runs on whatever port Render provides
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)