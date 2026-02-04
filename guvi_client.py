import requests
import os

def send_final_report(session_id, is_scam, total_messages, intelligence, notes):
    """
    Sends the final extracted intelligence to the GUVI evaluation endpoint.
    """
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Ensure the intelligence dictionary has all mandatory keys
    # Even if they are empty lists, GUVI expects these keys to exist.
    formatted_intelligence = {
        "bankAccounts": intelligence.get("bankAccounts", []),
        "upiIds": intelligence.get("upiIds", []),
        "phishingLinks": intelligence.get("phishingLinks", []),
        "phoneNumbers": intelligence.get("phoneNumbers", []),
        "suspiciousKeywords": intelligence.get("suspiciousKeywords", ["urgent", "verify", "blocked"])
    }

    payload = {
        "sessionId": session_id,
        "scamDetected": is_scam,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": formatted_intelligence,
        "agentNotes": notes
    }

    # Use the same API key you used for your main API authentication
    # This is often required by hackathon endpoints for tracking
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("GUVI_SECRET_KEY", "YOUR_SECRET_API_KEY")
    }

    try:
        print(f"🚀 Sending final report for session: {session_id}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ GUVI Callback Successful!")
        else:
            print(f"⚠️ GUVI Callback failed with status: {response.status_code}, Response: {response.text}")
            
        return response.status_code
    except Exception as e:
        print(f"❌ Critical Callback Error: {e}")
        return None