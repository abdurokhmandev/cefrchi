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

async def get_feedback(transcript: str, topic: str, lang: str, part: int = 1) -> dict:
    try:
        # Part-specific instruction
        part_instruction = f"This is Part {part} of the Speaking test."
        if part == 2:
            part_instruction += " This was a long monologue (cue card)."
        elif part == 3:
            part_instruction += " This was an abstract discussion."

        with open("speaking_prompt.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read().replace("{LANG}", lang)

        full_prompt = f"{system_prompt}\n\nCONTEXT: {part_instruction}\nTOPIC: {topic}\nTRANSCRIPT: {transcript}"
        
        response = model.generate_content(full_prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        
        if "error" in data:
            return {"error": data['error'], "band": "—", "cefr": "—", "feedback": data['error'], "grammar": "", "vocab": ""}

        # Star mapping for visual feedback
        def get_stars(score):
            try:
                s = float(score)
                filled = round(s / 2) # 9 band scale to 5 stars
                return "★" * filled + "☆" * (5 - filled)
            except:
                return "☆☆☆☆☆"

        # Format feedback text for Telegram
        fb = f"📊 <b>Sessiya natijalari:</b>\n"
        fb += f"  Ravonlik (Fluency):      [{get_stars(data['scores']['fluency'])}]\n"
        fb += f"  Lug'at (Vocabulary):     [{get_stars(data['scores']['lexical'])}]\n"
        fb += f"  Grammatika (Grammar):    [{get_stars(data['scores']['grammar'])}]\n"
        fb += f"  Izchillik (Coherence):   [{get_stars(data['scores'].get('coherence', data['scores']['fluency']))}]\n\n"
        
        fb += f"Taxminiy daraja: {data['cefr_level']} / IELTS ~{data['overall_band']}\n\n"
        fb += f"💡 <b>Tavsiya:</b> {data['key_tip']}"

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

async def detect_level(transcripts: list) -> str:
    """Detect user level based on 3 speaking answers"""
    try:
        combined_text = "\n\n".join([f"Q{i+1}: {t}" for i, t in enumerate(transcripts)])
        prompt = f"""
        Analyze these 3 English speaking answers and determine the CEFR level (A1, A2, B1, B2, C1, or C2).
        Be realistic. If answers are very short, it's A1 or A2.
        
        ANSWERS:
        {combined_text}
        
        Return ONLY the level (e.g., B2).
        """
        response = model.generate_content(prompt)
        level = response.text.strip()
        # Ensure it's a valid level
        for l in ['C2', 'C1', 'B2', 'B1', 'A2', 'A1']:
            if l in level:
                return l
        return "B1" # Default
    except:
        return "B1"

def progress_bar(score_str: str) -> str:
    try:
        score = float(score_str.split('/')[0])
        filled = round(score)
        empty = 9 - filled
        return "█" * filled + "░" * empty
    except:
        return "░" * 9

