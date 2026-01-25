import os
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

# Import your custom logic from other files
from engine import extract_raw_intel, get_scam_score
from guvi_client import send_final_report 
from persona import get_ai_response  # <--- Integrated AI Persona

app = FastAPI(title="Scam Honeypot API")

# --- 1. Define Request Models ---

class MessageData(BaseModel):
    text: str

class ChatRequest(BaseModel):
    sessionId: str
    message: MessageData
    conversationHistory: List[dict] = []

# --- 2. Define the POST Endpoint ---

@app.post("/chat")
async def handle_message(payload: ChatRequest, x_api_key: Optional[str] = Header(None)):
    """
    Endpoint for the GUVI Honeypot to send scammer messages.
    """
    
    # A. Security Check
    EXPECTED_KEY = os.getenv("YOUR_SECRET_KEY")
    if x_api_key != EXPECTED_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Invalid API Key. Check your Render Environment Variables."
        )

    # B. Extract Input Data
    msg_text = payload.message.text
    session_id = payload.sessionId
    history = payload.conversationHistory

    # C. Run Analysis (This fills the 'extractedIntelligence' box)
    is_scam, keywords = get_scam_score(msg_text)
    intel = extract_raw_intel(msg_text) # This now has phishingLinks, upiIds, etc.

    # D. Get AI Response (The 'Brain' logic)
    ai_reply = get_ai_response(msg_text, history)

    # E. Final Report Logic (The Callback)
    if "session_done" in msg_text or len(history) >= 5:
        send_final_report(
            session_id, 
            is_scam, 
            len(history) + 1, 
            intel, 
            "Scammer engaged and intelligence gathered."
        )

    # F. Return Response (The final JSON sent back to GUVI)
    return {
        "status": "success",
        "scamDetected": is_scam,
        "extractedIntelligence": intel, # <--- Corrected keys go here
        "message": {
            "text": ai_reply 
        }
    }

# --- 3. Local Run Config ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)