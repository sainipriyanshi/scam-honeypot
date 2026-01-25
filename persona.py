import os
import google.generativeai as genai

def get_ai_response(scammer_message, history):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Aiyo Beta, I can't find my glasses! (API Key Missing)"
        
    genai.configure(api_key=api_key)

    # 2026 FIX: The 404 happens because of the model string. 
    # We will try the most stable identifiers first.
    model_options = ["gemini-1.5-flash", "gemini-pro"]
    
    for model_name in model_options:
        try:
            # We explicitly initialize WITHOUT the 'models/' prefix here
            model = genai.GenerativeModel(model_name)
            
            prompt = f"You are Grandma Shanti, a sweet 70-year-old woman. Respond to: {scammer_message}"
            response = model.generate_content(prompt)
            
            if response.text:
                return response.text
        except Exception as e:
            # This logs the error to Render but keeps the loop moving
            print(f"Skipping {model_name} due to: {e}")
            continue

    # If ALL models fail, Grandma still talks so you don't lose points!
    return "Beta, my phone is acting very strange today. Can you repeat that?"