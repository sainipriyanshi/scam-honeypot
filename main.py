from fastapi import FastAPI, Header, Request, HTTPException
from engine import extract_raw_intel, get_scam_score
from guvi_client import send_final_report 
import os

app = FastAPI()

@app.post("/chat")
async def handle_message(request: Request, x_api_key: str = Header(None)):
    # 1. Security Check: Matches the 'Key' you set in Render
    EXPECTED_KEY = os.getenv("YOUR_SECRET_KEY") 
    
    if x_api_key != EXPECTED_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # 2. Parse Incoming Data
    data = await request.json()
    msg_text = data["message"]["text"]
    session_id = data.get("sessionId")
    history = data.get("conversationHistory", [])
    
    # 3. Analyze for Scam Intent
    is_scam, keywords = get_scam_score(msg_text)
    intel = extract_raw_intel(msg_text)
    
    # 4. Mandatory Callback Logic
    # We trigger the final report if the scammer says something specific 
    # or the conversation reaches a certain length.
    if "session_done" in msg_text or len(history) > 5: 
        # Sending all 5 required arguments to guvi_client
        send_final_report(
            session_id, 
            is_scam, 
            len(history) + 1, 
            intel, 
            "Agent successfully engaged scammer."
        )

    # 5. Response back to the GUVI Tester
    return {
        "status": "success",
        "scamDetected": is_scam,
        "extractedIntelligence": intel,
        "message": {"text": "I'm a bit confused, what do I need to do with my bank account?"}
    }