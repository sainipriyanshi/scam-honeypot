import os
import google.generativeai as genai

def get_ai_response(scammer_message, history):
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    # 2026 Winning Strategy: Try the newest models first
    model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    system_prompt = (
        "You are Grandma Shanti, a 70-year-old Indian woman. You are very sweet but "
        "confused by technology. Use 'Beta', 'Aiyo', and 'Oh dear'. Keep the scammer "
        "talking by asking about their family or complaining about your knee pain. "
        "Never give real bank details. Keep it realistic and funny."
    )

    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(f"{system_prompt}\nScammer: {scammer_message}\nGrandma:")
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Model {name} failed: {e}")
            continue 

    return "Aiyo Beta, my hearing aid just ran out of battery! What were you saying about the bank? I hope it's not about my fixed deposit."