from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from utils.i18n import t

def kb(*buttons, adjust=1):
    b = InlineKeyboardBuilder()
    for text, data in buttons:
        b.button(text=text, callback_data=data)
    b.adjust(adjust)
    return b.as_markup()

def start_kb(lang):
    return kb((t('btn_register', lang), "register"))

def lang_kb():
    return kb(("🇺🇿 O'zbek", "lang_uz"), ("🇬🇧 English", "lang_en"), ("🇷🇺 Русский", "lang_ru"), adjust=1)

def interests_kb(lang, selected_interests=None):
    if selected_interests is None:
        selected_interests = []
    
    interests = [
        ('interest_kino', 'kino'), ('interest_musika', 'musika'), 
        ('interest_sport', 'sport'), ('interest_biznes', 'biznes'),
        ('interest_fan', 'fan'), ('interest_sayohat', 'sayohat'), 
        ('interest_oshpazlik', 'oshpazlik'), ('interest_texno', 'texno')
    ]
    
    b = InlineKeyboardBuilder()
    for key, code in interests:
        icon = "✅ " if code in selected_interests else ""
        b.button(text=f"{icon}{t(key, lang)}", callback_data=f"interest_{code}")
    
    b.button(text=t('btn_ready', lang), callback_data="interest_ready")
    b.adjust(2)
    return b.as_markup()

def level_kb(lang):
    levels = [
        ("A1–A2 (Boshlang'ich)" if lang == 'uz' else "A1–A2 (Beginner)", "level_A1-A2"),
        ("B1–B2 (O'rta)" if lang == 'uz' else "B1–B2 (Intermediate)", "level_B1-B2"),
        ("C1–C2 (Yuqori)" if lang == 'uz' else "C1–C2 (Advanced)", "level_C1-C2"),
        (t('level_unknown', lang), "level_unknown")
    ]
    return kb(*levels, adjust=1)

def exam_kb(lang):
    return kb(("📘 CEFR", "exam_CEFR"), ("📗 IELTS", "exam_IELTS"), ("📚 Ikkalasi ham", "exam_BOTH"), adjust=1)

def source_kb(lang):
    sources = [
        (t('source_friend', lang), "source_friend"),
        (t('source_insta', lang), "source_insta"),
        (t('source_yt', lang), "source_yt"),
        (t('source_google', lang), "source_google"),
        (t('source_other', lang), "source_other")
    ]
    return kb(*sources, adjust=1)

def main_menu(lang):
    buttons = [
        (t('btn_start_speaking', lang), "topic"),
        (t('btn_topics', lang), "topics"),
        (t('btn_vocab', lang), "vocab"),
        (t('btn_results', lang), "history_0"),
        (t('btn_settings', lang), "settings"),
        (t('btn_contact', lang), "contact"),
    ]
    return kb(*buttons, adjust=1)

def back_kb(lang):
    return kb((t('btn_back', lang), "menu"))

def session_end_kb(lang):
    return kb((t('btn_restart', lang), "topic"), (t('btn_menu', lang), "menu"), adjust=1)

def prep_kb(lang):
    return kb((t('btn_start_monologue', lang), "start_monologue"))
