import httpx
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from persona import get_ai_response

app = FastAPI()

# 1. ADD YOUR MODEL HERE (Gatekeeper for incoming data)
class ChatRequest(BaseModel):
    sessionId: Optional[str] = "unknown" 
    message: Any 
    conversationHistory: Optional[list] = []
    metadata: Optional[Dict[str, Any]] = None

# Callback function remains the same
async def send_guvi_callback(session_id, scam_detected, intel):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": 1,
        "extractedIntelligence": intel,
        "agentNotes": "Scammer engaged via Grandma Shanti."
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"Callback failed: {e}")

# 2. UPDATE YOUR ROUTE (Use the model as a parameter)
@app.post("/chat")
async def chat(request_data: ChatRequest, background_tasks: BackgroundTasks):
    # FastAPI has already validated the body and put it into 'request_data'
    session_id = request_data.sessionId
    
    # Safely get text even if message is a dict or string
    raw_message = request_data.message
    if isinstance(raw_message, dict):
        message_text = raw_message.get("text", "")
    else:
        message_text = str(raw_message)

    history = request_data.conversationHistory

    # AI Response
    ai_reply = get_ai_response(message_text, history)

    # Intel Extraction logic
    intel = {"upiIds": ["scammer@upi"], "phishingLinks": []}

    # Mandatory Callback
    background_tasks.add_task(send_guvi_callback, session_id, True, intel)

    return {
        "status": "success",
        "scamDetected": True,
        "message": {"text": ai_reply},
        "extractedIntelligence": intel
    }

@app.get("/")
def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)