from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def kb(*buttons, adjust=1):
    b = InlineKeyboardBuilder()
    for text, data in buttons:
        b.button(text=text, callback_data=data)
    b.adjust(adjust)
    return b.as_markup()

def main_menu(lang):
    buttons = [
        ("🎤 Speaking boshlash" if lang == 'uz' else "🎤 Start Speaking", "topic"),
        ("📊 Mening natijalarim" if lang == 'uz' else "📊 My results", "history_0"),
        ("⚙️ Sozlamalar" if lang == 'uz' else "⚙️ Settings", "settings"),
    ]
    return kb(*buttons)

def settings_menu(lang):
    buttons = [
        ("🌐 Tilni o'zgartirish" if lang == 'uz' else "🌐 Change Language", "set_lang"),
        ("📈 Darajani o'zgartirish" if lang == 'uz' else "📈 Change Level", "set_level"),
        ("🎯 Imtihonni o'zgartirish" if lang == 'uz' else "🎯 Change Exam", "set_exam"),
        ("🏠 Bosh menyu" if lang == 'uz' else "🏠 Main Menu", "menu"),
    ]
    return kb(*buttons)

def lang_kb():
    return kb(("🇺🇿 O'zbek", "lang_uz"), ("🇬🇧 English", "lang_en"), adjust=2)

def level_kb():
    return kb(("A1", "level_A1"), ("A2", "level_A2"), ("B1", "level_B1"), 
              ("B2", "level_B2"), ("C1", "level_C1"), ("C2", "level_C2"), adjust=3)

def exam_kb():
    return kb(("IELTS", "exam_IELTS"), ("CEFR", "exam_CEFR"), ("Ikkalasi / Both", "exam_ALL"), adjust=1)

def part_kb(lang):
    return kb(
        ("Part 1", "part_1"), ("Part 2", "part_2"), ("Part 3", "part_3"),
        ("Tasodifiy" if lang == 'uz' else "Random", "part_0"),
        ("🏠 Menu", "menu"), adjust=2
    )
