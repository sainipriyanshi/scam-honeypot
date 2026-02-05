import os
import random
from google import genai

def get_ai_response(scammer_message, history):
    api_key = os.getenv("GEMINI_API_KEY")
    responses = [
        "Arey bhai, please don't block my account! What do I need to do?",
        "I am trying to open the app but it is very slow. Can you help me?",
        "Which SBI branch are you calling from? I will come there tomorrow.",
        "Oh no! My wife will be so angry if the account is blocked. Please wait.",
        "I am typing the OTP but it says invalid. Can you send it again?"
    ]
    
    # Return a random response to look "human"
    return random.choice(responses)

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # New Persona: Aman (Normal Customer)
        # Strategy: Act worried/cooperative to lure the scammer into giving their details.
        system_instruction = (
            "You are Aman, a regular 30-year-old customer. You just received a message regarding your bank/UPI. "
            "You are slightly panicked but willing to cooperate. "
            "Your goal is to be a 'Honeypot': act like you don't know how to use the app well so the scammer "
            "is forced to give you THEIR Bank Account number, UPI ID, or Phone Number to 'help' you. "
            "Keep your responses concise and realistic. Do not reveal you are an AI."
        )

        # Formatting the conversation context
        prompt = f"""
        System Role: {system_instruction}
        
        Conversation History:
        {history}
        
        Latest Scammer Message: "{scammer_message}"
        
        Aman's Response:"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system_instruction}\n\nScammer: {scammer_message}\n\nAman:"
        )
        
        return response.text

    except Exception as e:
        print(f"Gemini 2.0 Error: {e}")
        return "The connection is weak, could you please send that again?"