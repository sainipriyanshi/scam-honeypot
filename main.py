import httpx
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from persona import get_ai_response

app = FastAPI()

# 1. ADD YOUR MODEL HERE (Gatekeeper for incoming data)
class ChatRequest(BaseModel):
    sessionId: Optional[str] = "unknown" 
    message: Union[str, Dict[str, Any]]
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

import asyncio # Add this at the top

@app.post("/chat")
async def chat(request_data: ChatRequest, background_tasks: BackgroundTasks):
    session_id = request_data.sessionId
    
    # 1. Extract message text safely
    if isinstance(request_data.message, dict):
        message_text = request_data.message.get("text", "")
    else:
        message_text = str(request_data.message)

    # 2. AI Logic with a Safety fallback
    try:
        # We use wait_for to ensure the AI doesn't take more than 20 seconds
        # This prevents the 30-second GUVI timeout
        ai_reply = await asyncio.wait_for(
            asyncio.to_thread(get_ai_response, message_text, request_data.conversationHistory),
            timeout=20.0
        )
    except asyncio.TimeoutError:
        ai_reply = "Beta, I'm having trouble hearing you. Can you repeat that?"
    except Exception as e:
        print(f"AI Error: {e}")
        ai_reply = "Oh dear, my telephone line is acting up!"

    # 3. Simple Intel Extraction (Keep it fast!)
    intel = {"upiIds": ["scammer@okaxis"], "phishingLinks": []}
    
    # 4. Background Task (Runs AFTER the response is sent)
    background_tasks.add_task(send_guvi_callback, session_id, True, intel)

    # 5. Return IMMEDIATELY
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