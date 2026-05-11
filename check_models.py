from google import genai
from config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)

print("Sizning API kalitingiz uchun mavjud modellar:")
try:
    for model in client.models.list():
        print(f"- {model.name} (Support: {model.supported_methods})")
except Exception as e:
    print(f"Xatolik: {e}")
