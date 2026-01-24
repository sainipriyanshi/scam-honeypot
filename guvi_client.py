import requests

def send_final_report(session_id, is_scam, total_messages, intelligence, notes):
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    payload = {
        "sessionId": session_id,
        "scamDetected": is_scam,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": notes
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code
    except Exception as e:
        print(f"Callback failed: {e}")
        return None