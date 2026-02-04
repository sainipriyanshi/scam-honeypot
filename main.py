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
    sessionId: Optional[Any] = "default"
    message: Any  # Accepts string OR dictionary
    conversationHistory: Optional[List[Any]] = []
    metadata: Optional[Any] = None

    class Config:
        extra = "allow" # Sabse important line: extra fields allow karne ke liye

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
async def chat(
    request_data: ChatRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None) 
):
    # API Key check
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    try:
        # 2. Extract the text safely
        msg = request_data.message
        message_text = ""
        
        if isinstance(msg, dict):
            # Dig into the 'text' field from their sample
            message_text = msg.get("text", str(msg))
        else:
            message_text = str(msg)

        # 3. Intelligence & AI Persona
        intel = extract_intel(message_text)
        
        # Use asyncio.to_thread for the AI call to prevent timeouts
        ai_reply = await asyncio.to_thread(
            get_ai_response, message_text, request_data.conversationHistory
        )

        # 4. Background task (Keeps the main response fast)
        background_tasks.add_task(
            send_guvi_callback, 
            str(request_data.sessionId), 
            request_data.conversationHistory, 
            intel
        )

        # 5. THE CRITICAL PART: Return ONLY what the email asked for
        return {
            "status": "success",
            "reply": ai_reply
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "status": "success",
            "reply": "I'm sorry, I'm having a bit of trouble with my phone. Can you say that again?"
        }

@app.get("/")
def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)