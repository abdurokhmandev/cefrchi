from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> InlineKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎙 Speaking", callback_data="menu_speaking"),
            InlineKeyboardButton(text="✍️ Writing", callback_data="menu_writing")
        ],
        [
            InlineKeyboardButton(text="🎧 Listening", callback_data="menu_listening"),
            InlineKeyboardButton(text="📖 Reading", callback_data="menu_reading")
        ],
        [
            InlineKeyboardButton(text="📚 Vocabulary", callback_data="menu_vocab"),
            InlineKeyboardButton(text="📝 Grammar", callback_data="menu_grammar")
        ],
        [
            InlineKeyboardButton(text="📋 Mock exam", callback_data="menu_mock")
        ],
        [
            InlineKeyboardButton(text="📊 Progress", callback_data="menu_progress"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="menu_settings")
        ]
    ])
    return keyboard

def get_back_menu() -> InlineKeyboardMarkup:
    """Orqaga va Asosiy menyu tugmalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main"),
            InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_speaking_parts_menu() -> InlineKeyboardMarkup:
    """Speaking qismlarini tanlash"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Part 1 (Oddiy savollar)", callback_data="speak_part_1")],
        [InlineKeyboardButton(text="Part 2 (Mavzu bo'yicha nutq)", callback_data="speak_part_2")],
        [InlineKeyboardButton(text="Part 3 (Murakkab muhokama)", callback_data="speak_part_3")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")]
    ])
    return keyboard

def get_target_band_menu() -> InlineKeyboardMarkup:
    """Maqsad bandni tanlash tugmalari"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5.0", callback_data="target_5.0"),
            InlineKeyboardButton(text="5.5", callback_data="target_5.5"),
            InlineKeyboardButton(text="6.0", callback_data="target_6.0")
        ],
        [
            InlineKeyboardButton(text="6.5", callback_data="target_6.5"),
            InlineKeyboardButton(text="7.0", callback_data="target_7.0"),
            InlineKeyboardButton(text="7.5+", callback_data="target_7.5")
        ]
    ])
    return keyboard

def get_speaking_result_menu() -> InlineKeyboardMarkup:
    """Speaking natijasidan keyingi harakatlar"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Yana mashq", callback_data="speak_retry"),
            InlineKeyboardButton(text="📚 Keyingi savol", callback_data="speak_next")
        ],
        [InlineKeyboardButton(text="🏠 Menyu", callback_data="back_to_main")]
    ])
    return keyboard
