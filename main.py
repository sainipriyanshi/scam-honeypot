from fastapi import FastAPI, Header, Request
from engine import extract_raw_intel, get_scam_score
from guvi_client import send_final_report # Implementation of the callback

app = FastAPI()

@app.post("/chat")
async def handle_message(request: Request, x_api_key: str = Header(None)):
    data = await request.json()
    msg_text = data["message"]["text"]
    
    is_scam, keywords = get_scam_score(msg_text)
    intel = extract_raw_intel(msg_text)
    
    # Logic to decide if the conversation is over
    if "session_done" in msg_text: # Example trigger
        send_final_report(data["sessionId"], intel, "Scammer gave up.")

    return {
        "status": "success",
        "scamDetected": is_scam,
        "extractedIntelligence": intel,
        "message": {"text": "Oh dear, my account? What should I do?"}
    }