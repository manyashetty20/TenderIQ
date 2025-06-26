import os
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY missing. Please set it in .env or environment variables.")
    exit(1)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def get_groq_response(prompt: str) -> tuple[str, float]:
    try:
        # Prepare prompt
        trimmed_prompt = prompt.strip()[:3500]

        print(f"\n📤 Prompt to Groq (length: {len(trimmed_prompt)} chars):\n", trimmed_prompt)

        start = time.perf_counter()
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a tender document assistant."},
                {"role": "user", "content": trimmed_prompt}
            ],
            temperature=0.3,
            max_tokens=512,
            timeout=60
        )
        end = time.perf_counter()

        answer = response.choices[0].message.content.strip()
        print("\n✅ Groq Output:\n", answer)
        return answer, round(end - start, 3)

    except Exception as e:
        print("❌ Groq Error:", e)
        return f"⚠️ Groq Error: {str(e)}", 0.0
