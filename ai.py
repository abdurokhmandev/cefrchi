import google.generativeai as genai
from config import GOOGLE_API_KEY
import os
import time

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-flash-latest')

async def transcribe(audio_path: str) -> str:
    try:
        audio_file = genai.upload_file(path=audio_path)
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        response = model.generate_content([
            "Transcribe this audio into English text. Only output the transcript.",
            audio_file
        ])
        genai.delete_file(audio_file.name)
        return response.text.strip()
    except Exception as e:
        print(f"STT Error: {e}")
        return ""

import json

async def get_feedback(transcript: str, topic: str, lang: str) -> dict:
    try:
        with open("speaking_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read().replace("{LANG}", lang)

        full_prompt = f"{system_prompt}\n\nTOPIC: {topic}\nTRANSCRIPT: {transcript}"
        
        response = model.generate_content(full_prompt)
        text = response.text.strip()
        
        # Clean markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        
        if "error" in data:
            return {"error": data['error'], "band": "—", "cefr": "—", "feedback": data['error'], "grammar": "", "vocab": ""}

        # Format feedback text for Telegram
        fb = f"🎯 <b>IELTS Band: {data['overall_band']}/9</b>\n"
        fb += f"📊 <b>CEFR Level: {data['cefr_level']}</b>\n\n"
        fb += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        fb += f"{data['detailed_feedback']}\n\n"
        
        fb += "✅ <b>Ballar:</b>\n"
        fb += f"• Fluency: {data['scores']['fluency']}/9\n"
        fb += f"• Lexical: {data['scores']['lexical']}/9\n"
        fb += f"• Grammar: {data['scores']['grammar']}/9\n"
        fb += f"• Pronunciation: {data['scores']['pronunciation']}/9\n\n"
        
        fb += "💡 <b>Asosiy maslahat:</b>\n"
        fb += f"<i>{data['key_tip']}</i>"

        grammar_tips = "\n".join([f"• {x}" for x in data.get('grammar_corrections', [])])
        vocab_tips = "\n".join([f"• {x}" for x in data.get('vocabulary_suggestions', [])])

        return {
            "full_text": fb,
            "band": data['overall_band'],
            "cefr": data['cefr_level'],
            "grammar": grammar_tips,
            "vocab": vocab_tips,
            "raw_data": data
        }
    except Exception as e:
        print(f"Feedback Error: {e}")
        return {"error": str(e), "band": "—", "cefr": "—", "feedback": f"Xatolik: {e}", "grammar": "", "vocab": ""}


def progress_bar(score_str: str) -> str:
    try:
        score = float(score_str.split('/')[0])
        filled = round(score)
        empty = 9 - filled
        return "█" * filled + "░" * empty
    except:
        return "░" * 9
