
# ================= GEMINI =================
from google import genai
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents="Reply with OK"
    )

    print("✅ Gemini working:", response.text)

except Exception as e:
    print("❌ Gemini error:", e)


