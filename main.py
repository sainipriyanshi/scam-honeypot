import os
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

# Import your custom logic
from engine import extract_raw_intel, get_scam_score
from guvi_client import send_final_report 

app = FastAPI(title="Scam Honeypot API")

# --- 1. HEALTH CHECK ROUTES (Fixes the 404 errors) ---

@app.get("/")
@app.get("/health")
def home():
    """
    Returns a 200 OK status to keep the hosting provider happy.
    """
    return {
        "status": "online", 
        "message": "Scam Honeypot API is running",
        "version": "1.0.0"
    }

# --- 2. Define Request Models ---

class MessageData(BaseModel):
    text: str

class ChatRequest(BaseModel):
    sessionId: str
    message: MessageData
    conversationHistory: List[dict] = []

# --- 3. Define the POST Endpoint ---

@app.post("/chat")
async def handle_message(payload: ChatRequest, x_api_key: Optional[str] = Header(None)):
    """
    Endpoint for the GUVI Honeypot to send scammer messages.
    """
    # Security Check
    EXPECTED_KEY = os.getenv("YOUR_SECRET_KEY")
    if x_api_key != EXPECTED_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key.")

    # Data Extraction
    msg_text = payload.message.text
    session_id = payload.sessionId
    history = payload.conversationHistory

    # Analysis Logic
    is_scam, keywords = get_scam_score(msg_text)
    intel = extract_raw_intel(msg_text)

    # Final Report Logic
    if "session_done" in msg_text or len(history) >= 5:
        send_final_report(
            session_id, 
            is_scam, 
            len(history) + 1, 
            intel, 
            "Scammer engaged and intelligence gathered."
        )

    return {
        "status": "success",
        "scamDetected": is_scam,
        "extractedIntelligence": intel,
        "message": {
            "text": "Wait, I'm confused. My account is blocked? How can I verify it without my password?"
        }
    }

# --- 4. Local Run Config ---
if __name__ == "__main__":
    import uvicorn
    # Changed port to 10000 to match your Uvicorn logs
    uvicorn.run(app, host="0.0.0.0", port=10000)