import json
import logging
from openai import AsyncOpenAI
from config import config
from .grader import SPEAKING_SYSTEM_PROMPT, WRITING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# OpenRouter uchun maxsus client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.openrouter_api_key.get_secret_value()
)

MODELS = [
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemini-flash-1.5"
]

async def _call_openrouter(messages: list) -> dict:
    """Asosiy model, xato yoki 429 bo'lsa fallback modellar orqali so'rov yuboradi"""
    headers = {
        "HTTP-Referer": "https://t.me/ielts_cefr_bot",
        "X-Title": "IELTS CEFR Bot"
    }

    for model in MODELS:
        try:
            logger.info(f"OpenRouter so'rovi yuborilmoqda... Model: {model}")
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                extra_headers=headers,
                timeout=30.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            
            # JSON parsirovka
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Agar to'g'ri JSON formatida qaytarmasa
                logger.warning(f"JSON parsing error: {content}")
                
                # O'zgaruvchilarni ajratish (fallback o'rnida regex bo'lishi mumkin)
                pass

        except Exception as e:
            logger.warning(f"Model {model} bilan xatolik yuz berdi: {e}")
            continue
            
    raise Exception("Barcha modellar xato qaytardi (OpenRouter).")

async def grade_speaking(transcript: str, question: str, part: int) -> dict:
    """
    Speaking javobini baholaydi.
    Qaytaradi: {fluency, lexical, grammar, pronunciation, overall,
                feedback_uz, strengths: list[str], improvements: list[str],
                corrected_sample: str}
    """
    messages = [
        {"role": "system", "content": SPEAKING_SYSTEM_PROMPT},
        {"role": "user", "content": f"Part: {part}\nQuestion: {question}\nCandidate Transcript: {transcript}"}
    ]
    return await _call_openrouter(messages)

async def grade_writing(essay: str, task_type: str, prompt: str) -> dict:
    """
    Essay ni baholaydi.
    Qaytaradi: {task_achievement/task_response, coherence, lexical, grammar, overall, ...}
    """
    messages = [
        {"role": "system", "content": WRITING_SYSTEM_PROMPT},
        {"role": "user", "content": f"Task Type: {task_type}\nPrompt: {prompt}\nCandidate Essay: {essay}"}
    ]
    return await _call_openrouter(messages)

async def generate_speaking_question(cefr_level: str, part: int, topic: str = None) -> dict:
    """
    Yangi speaking savol yaratadi.
    Qaytaradi: {question: str, follow_up: list[str], tips: str}
    """
    prompt = f"Generate an IELTS Speaking Part {part} question suitable for a {cefr_level} student."
    if topic:
        prompt += f" The topic should be related to: {topic}."
    prompt += "\nRespond ONLY in valid JSON: {\"question\": \"...\", \"follow_up\": [\"...\", \"...\"], \"tips\": \"...\"}"
    
    messages = [
        {"role": "system", "content": "You are an IELTS test creator."},
        {"role": "user", "content": prompt}
    ]
    return await _call_openrouter(messages)

async def explain_grammar(topic: str, cefr_level: str, mistake: str) -> dict:
    """
    Grammatika xatosini tushuntiradi.
    Qaytaradi: {rule: str, explanation_uz: str, examples: list[str], exercise: str}
    """
    prompt = f"Explain this grammar mistake for a {cefr_level} student. Topic: {topic}. Mistake: {mistake}."
    prompt += "\nRespond ONLY in valid JSON: {\"rule\": \"...\", \"explanation_uz\": \"O'zbekcha tushuntirish\", \"examples\": [\"...\"], \"exercise\": \"...\"}"
    
    messages = [
        {"role": "system", "content": "You are an expert English grammar teacher."},
        {"role": "user", "content": prompt}
    ]
    return await _call_openrouter(messages)
