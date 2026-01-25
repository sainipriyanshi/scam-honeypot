import os
import google.generativeai as genai

def get_ai_response(scammer_message, history):
    try:
        # Move configuration inside to prevent startup hangs
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Oh dear, my telephone line is cut! (Check API Key)"
            
        genai.configure(api_key=api_key)
        
        # Use the most basic model name for maximum compatibility
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"You are Grandma Shanti, a confused 70-year-old. Respond to: {scammer_message}"
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Error: {e}")
        return "Wait, beta... my glasses are missing. What did you say?"