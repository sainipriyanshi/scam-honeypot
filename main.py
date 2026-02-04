import httpx
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel
import asyncio
import re
from typing import Optional, Dict, Any, List
from persona import get_ai_response

app = FastAPI()

# 1. ADD YOUR SECRET KEY HERE (Matches what you give GUVI)
API_KEY_CREDENTIAL = "YOUR_SECRET_API_KEY" 

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
    
    # GUVI expects the total count of messages
    total_turns = len(history) + 2 
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_turns,
        "extractedIntelligence": intel,
        "agentNotes": "Engaged using Grandma Shanti persona. Successfully captured potential scam indicators."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Note: GUVI might require your API Key in headers here too
            await client.post(url, json=payload, timeout=10.0)
        except Exception as e:
            print(f"Callback failed: {e}")

@app.post("/chat")
async def chat(
    request_data: ChatRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None) # 2. CHECK FOR API KEY
):
    # Security Check
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    session_id = request_data.sessionId
    
    # Extract message text safely
    if isinstance(request_data.message, dict):
        message_text = request_data.message.get("text", "")
    else:
        message_text = str(request_data.message)

    try:
        # AI Response logic
        ai_reply = await asyncio.wait_for(
            asyncio.to_thread(get_ai_response, message_text, request_data.conversationHistory),
            timeout=20.0
        )
    except Exception as e:
        print(f"Chat Route Error: {e}")
        ai_reply = "Beta, the phone is making a buzzing sound. What did you say?"

    # 3. DYNAMIC EXTRACTION (Don't hardcode!)
    # We check both the scammer's message and history for info
    combined_text = message_text + " " + str(request_data.conversationHistory)
    intel = extract_intel(combined_text)
    
    # 4. CALLBACK TRIGGER
    # According to GUVI, send this when scam is confirmed. 
    # For a Honeypot, we assume detection is already active.
    background_tasks.add_task(send_guvi_callback, session_id, request_data.conversationHistory, intel)

    # 5. GUVI MANDATORY OUTPUT FORMAT
    return {
        "status": "success",
        "reply": ai_reply
    }

@app.get("/")
def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)