import httpx
from fastapi import FastAPI, Request, BackgroundTasks
from persona import get_ai_response

app = FastAPI()

# This function sends the mandatory data to GUVI
async def send_guvi_callback(session_id, scam_detected, intel):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": 1, # Update this if you track history
        "extractedIntelligence": intel,
        "agentNotes": "Scammer used urgency tactics. Grandma engaged successfully."
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"Callback failed: {e}")

@app.post("/chat")
async def chat(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    session_id = data.get("sessionId")
    message_text = data.get("message", {}).get("text", "")

    # 1. Your existing Intel Extraction logic here...
    # (Assuming you have your regex logic for upiIds, phishingLinks, etc.)
    intel = {
        "bankAccounts": [], 
        "upiIds": ["verify@upi"], # Use your regex results here
        "phishingLinks": ["http://scam.com"],
        "phoneNumbers": [],
        "suspiciousKeywords": ["blocked", "urgent"]
    }
    
    # 2. Get the AI Persona Response
    ai_text = get_ai_response(message_text, [])

    # 3. MANDATORY: Trigger the GUVI callback in the background
    background_tasks.add_task(send_guvi_callback, session_id, True, intel)

    return {
        "status": "success",
        "scamDetected": True,
        "extractedIntelligence": intel,
        "message": {"text": ai_text}
    }

# --- 3. Local Run Config ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)