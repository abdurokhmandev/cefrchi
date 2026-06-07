import json
import logging
from typing import Optional

from config import config
from .grader import SPEAKING_SYSTEM_PROMPT, WRITING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Try to initialize OpenRouter/OpenAI client only if API key is provided
_openrouter_key = getattr(config, "openrouter_api_key", None)
client = None

if _openrouter_key:
    try:
        try:
            api_key = _openrouter_key.get_secret_value()
        except Exception:
            api_key = str(_openrouter_key)

        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        logger.info("OpenRouter client initialized.")
    except Exception as e:
        client = None
        logger.warning(f"Failed to initialize OpenRouter client: {e}")
else:
    logger.warning("OPENROUTER API key not set — OpenRouter client disabled. Grading/generation features will use fallbacks.")

MODELS = [
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemini-flash-1.5"
]


async def _call_openrouter(messages: list) -> dict:
    """Asosiy model, xato yoki 429 bo'lsa fallback modellar orqali so'rov yuboradi"""
    if not client:
        # Fallback: return an informative error dict to the caller
        return {"error": "OpenRouter client not configured", "detail": "Set OPENROUTER API key or configure service."}

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
                # Continue to next model
                continue

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

    res = await _call_openrouter(messages)
    if res is None or res.get("error"):
        # Provide a graceful fallback so the bot doesn't crash
        return {
            "fluency": 0.0,
            "lexical": 0.0,
            "grammar": 0.0,
            "pronunciation": 0.0,
            "overall": 0.0,
            "feedback_uz": "OpenRouter xizmatiga ulanib bo‘lmadi. Iltimos, keyinroq urinib ko‘ring.",
            "strengths": [],
            "improvements": [],
            "corrected_sample": ""
        }

    return res


async def grade_writing(essay: str, task_type: str, prompt: str) -> dict:
    """
    Essay ni baholaydi.
    Qaytaradi: {task_achievement/task_response, coherence, lexical, grammar, overall, ...}
    """
    messages = [
        {"role": "system", "content": WRITING_SYSTEM_PROMPT},
        {"role": "user", "content": f"Task Type: {task_type}\nPrompt: {prompt}\nCandidate Essay: {essay}"}
    ]

    res = await _call_openrouter(messages)
    if res is None or res.get("error"):
        return {
            "task_response": 0.0,
            "coherence": 0.0,
            "lexical": 0.0,
            "grammar": 0.0,
            "overall": 0.0,
            "feedback_uz": "OpenRouter xizmatiga ulanib bo‘lmadi. Iltimos, keyinroq urinib ko‘ring.",
        }

    return res


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

    res = await _call_openrouter(messages)
    if res is None or res.get("error"):
        # Fallback simple generator
        return {
            "question": "Tell me about your hometown.",
            "follow_up": ["What do you like about it?", "Has it changed recently?"],
            "tips": "Speak clearly, give examples, and expand your answers."
        }

    return res


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

    res = await _call_openrouter(messages)
    if res is None or res.get("error"):
        return {
            "rule": "",
            "explanation_uz": "OpenRouter xizmatiga ulanib bo‘lmadi.",
            "examples": [],
            "exercise": ""
        }

    return res
