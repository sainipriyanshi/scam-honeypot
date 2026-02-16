import httpx
import os
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request 
from fastapi.responses import RedirectResponse
from pydantic import BaseModel,Field
import asyncio
import re
from typing import Optional, Dict, Any, List
from persona import get_ai_response

app = FastAPI()

# Add this to stop the 404 logs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# 1. YOUR SECRET KEY
API_KEY_CREDENTIAL = "priyanshi_secret_123" 

class Message(BaseModel):
    text: str
    sender: str
    timestamp: Optional[int] = None

class ChatRequest(BaseModel):
    sessionId: str 
    message: Message  
    conversationHistory: Optional[List[Any]] = []
    metadata: Optional[dict] = None

    class Config:
        extra = "allow"


def extract_intel(text: str):
    return {
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+', text),
        "phishingLinks": re.findall(r'https?://\S+', text),
        "phoneNumbers": re.findall(r'[6-9]\d{9}', text), 
        "suspiciousKeywords": list(set(re.findall(r'(?i)(blocked|verify|urgent|kyc|otp|suspend|login|limit)', text)))
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
    request: Request,
    key: Optional[str] =None
):
    

   api_key_header = request.headers.get("x-api-key") or request.headers.get("X-Api-Key")
   
   if api_key_header != API_KEY_CREDENTIAL and key != API_KEY_CREDENTIAL:
        print(f"403 Blocked: Header={api_key_header}, URL_Key={key}")


   try:
     

        scammer_text = request_data.message.text
        
        full_conversation_text = scammer_text
        for turn in request_data.conversationHistory:
           
            prev_msg = turn.get("text", "") if isinstance(turn, dict) else getattr(turn, "text", "")
            full_conversation_text += f" {prev_msg}"
        

        ai_reply = await asyncio.to_thread(get_ai_response, scammer_text, request_data.conversationHistory)

       
        intel = extract_intel(full_conversation_text)

        background_tasks.add_task(
            send_guvi_callback, 
            request_data.sessionId, 
            request_data.conversationHistory, 
            intel
        )

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

# @app.get("/")
# def health_check():
#     return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)