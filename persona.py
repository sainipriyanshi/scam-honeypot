import os
from google import genai

def get_ai_response(scammer_message, history):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "I'm sorry, I'm having trouble connecting to the network right now."

    try:
        client = genai.Client(api_key=api_key, timeout=20)
        
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
            model="gemini-1.5-flash",
            contents=f"You are Aman. Respond to this scammer: {scammer_message}"
        )
        
        return response.text

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "The connection is weak, could you please send that again?"