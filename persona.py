import os
import google.generativeai as genai

def get_ai_response(scammer_message, history):
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # 2026 FIX: Use the 'models/' prefix if the short name fails
    # This is the most common reason for 404 errors
    model_names = ["models/gemini-1.5-flash", "gemini-1.5-flash", "models/gemini-pro"]
    
    # This prompt tells the AI exactly how to behave
    system_prompt = (
        "You are Grandma Shanti, a sweet 70-year-old Indian woman. "
        "A scammer is messaging you. Do not reveal you know it's a scam. "
        "Be confused. Ask them 'Beta, how do I click the link?' or 'Aiyo, my knee hurts, "
        "can we talk later?' Keep them engaged to waste their time."
    )

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            # Combine history and prompt for a real conversation
            response = model.generate_content(f"{system_prompt}\nScammer: {scammer_message}\nGrandma:")
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"DEBUG: {name} failed: {e}")
            continue 

    return "Beta, my phone screen is very blurry. Are you from the bank?"