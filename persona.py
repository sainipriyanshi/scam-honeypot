import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# 1. GCP Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID") 
LOCATION = "us-central1"  # Or "asia-south1" for Mumbai if your GCP project is set there

# Initialize Vertex AI once when the module loads
vertexai.init(project=PROJECT_ID, location=LOCATION)

def get_ai_response(scammer_message, history):
    """
    Uses GCP Vertex AI to generate the Aman persona response.
    """
    try:
        # 2. Initialize Model (Gemini 1.5 Flash is highly stable on Vertex)
        model = GenerativeModel("gemini-1.5-flash")
        
        # 3. Professional System Instructions + User Input
        prompt = (
            f"Context: You are Aman, a 30-year-old target of a scam. "
            f"Act confused and panicked to keep the scammer engaged. "
            f"Keep replies short and realistic.\n\n"
            f"Scammer says: {scammer_message}\n"
            f"Aman:"
        )

        # 4. Generation Configuration (Limits tokens to save costs/latency)
        config = GenerationConfig(
            max_output_tokens=150,
            temperature=0.7,
        )

        response = model.generate_content(prompt, generation_config=config)
        
        return response.text

    except Exception as e:
        # Log the error for Render debugging
        print(f"GCP Vertex AI Error: {str(e)}")
        
        # Friendly fallback so the user experience doesn't break
        return "Arey, wait... my phone is acting very strange. Kya bola aapne?"