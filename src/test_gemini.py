import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

response = client.interactions.create(
    model="gemini-3.8-flash",
    input="Say hello in one short sentence."
)

print("Gemini response:")
print(response.output_text)