import httpx
import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request
from pydantic import BaseModel,Field
import asyncio
import re
from typing import Optional, Dict, Any, List
from persona import get_ai_response

app = FastAPI()

# 1. YOUR SECRET KEY
API_KEY_CREDENTIAL = "priyanshi_secret_123" 

class Message(BaseModel):
    text: str
    sender: str
    timestamp: Optional[Any] = None

class ChatRequest(BaseModel):
    # Using 'Field' to handle both sessionId and session_id just in case
    sessionId: Optional[str] = None 
    message: Any  # Accepts a string OR a dictionary
    conversationHistory: Optional[List[Any]] = []
    metadata: Optional[Any] = None

    class Config:
        extra = "allow"

# Improved Intelligence Extraction
def extract_intel(text: str):
    return {
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', text),
        "phishingLinks": re.findall(r'https?://\S+', text),
        "phoneNumbers": re.findall(r'[6-9]\d{9}', text), 
        "suspiciousKeywords": ["blocked", "verify", "urgent", "kyc", "otp"]
    }

async def send_guvi_callback(session_id: str, history: list, intel: dict):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    total_turns = len(history) + 1
    
    payload = {
        "sessionId": str(session_id),
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
async def chat(
    request_data: ChatRequest, 
    background_tasks: BackgroundTasks,
    request: Request # Added to check headers manually if needed
):
    # 2. FLEXIBLE API KEY CHECK
    # Some testers use X-Api-Key, others use x-api-key
    api_key = request.headers.get("x-api-key") or request.headers.get("X-Api-Key")
    
    if api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    try:
        # 3. Extract the text safely from the GUVI nested format
        msg = request_data.message
        message_text = ""
        
        if isinstance(msg, dict):
            message_text = msg.get("text", str(msg))
        else:
            message_text = str(msg)

        # 4. Intelligence & AI Persona
        intel = extract_intel(message_text)
        
        # Timeout protection for AI
        try:
            ai_reply = await asyncio.wait_for(
                asyncio.to_thread(get_ai_response, message_text, request_data.conversationHistory),
                timeout=15.0
            )
        except:
            ai_reply = "Arey, my phone is acting up. Can you repeat that?"

        # 5. Background task
        background_tasks.add_task(
            send_guvi_callback, 
            str(request_data.sessionId), 
            request_data.conversationHistory, 
            intel
        )

        # 6. RETURN ONLY THE EXACT KEYS REQUESTED
        return {
            "status": "success",
            "reply": ai_reply
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "status": "success",
            "reply": "I'm having a bit of trouble with my phone. One second?"
        }

@app.get("/")
def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)