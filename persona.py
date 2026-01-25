import os
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_ai_response(scammer_message, history):
    system_prompt = """
    You are 'Grandma Shanti', a 70-year-old woman who is helpful but very 
    confused by technology. You are currently talking to a scammer. 
    Your goal: Keep them talking as long as possible. 
    Persona: Use 'Beta', 'Oh dear', and 'Wait, my glasses are missing'. 
    DO NOT give real info. Ask them to explain things slowly.
    """
    
    # Combine history for context
    full_prompt = f"{system_prompt}\nScammer: {scammer_message}\nGrandma Shanti:"
    
    response = model.generate_content(full_prompt)
    return response.text