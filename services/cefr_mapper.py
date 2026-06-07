def band_to_cefr(band: float) -> str:
    """IELTS Band score ni CEFR darajasiga o'zgartiradi."""
    if band <= 1.0:
        return "A1"
    elif 1.5 <= band <= 2.5:
        return "A1"
    elif 3.0 <= band <= 3.5:
        return "A2"
    elif band == 4.0:
        return "B1"
    elif 4.5 <= band <= 5.0:
        return "B1-B2"
    elif 5.5 <= band <= 6.0:
        return "B2"
    elif 6.5 <= band <= 7.0:
        return "C1"
    elif 7.5 <= band <= 8.0:
        return "C1-C2"
    elif 8.5 <= band <= 9.0:
        return "C2"
    return "N/A"

def cefr_description_uz(cefr: str) -> str:
    """CEFR darajasining o'zbekcha izohini qaytaradi."""
    descriptions = {
        "A1": "Boshlang'ich — asosiy iboralarni bilasiz",
        "A2": "Elementar — oddiy suhbat qilolasiz",
        "B1": "O'rta — tanish mavzularda gaplasha olasiz",
        "B1-B2": "O'rta — fikringizni ifodalay olasiz",
        "B2": "O'rta-yuqori — ravon muloqot qilasiz",
        "C1": "Ilg'or — murakkab mavzularda erkin gaplashasiz",
        "C1-C2": "Ilg'or — to'la ravon gaplashasiz",
        "C2": "Ustod — deyarli ona tili darajasida"
    }
    return descriptions.get(cefr, "Noaniq daraja")

def get_next_cefr_tips(current_cefr: str) -> list[str]:
    """Keyingi darajaga chiqish uchun aniq maslahatlar."""
    tips = {
        "A1": [
            "Kundalik iboralarni yod oling va ishlatib ko'ring.",
            "Sodda audio matnlarni eshitishni boshlang.",
            "Asosiy grammatik qoidalarni (Present Simple, to be) o'rganing."
        ],
        "A2": [
            "Vocabulary (so'z boyligini) har kuni 10 tadan yangi so'z bilan oshiring.",
            "Qisqa matnlarni o'qib, mazmunini tushunishga harakat qiling.",
            "Ingliz tilidagi oddiy videolarni subtitrlar bilan ko'ring."
        ],
        "B1": [
            "Fikringizni aniqroq ifodalash uchun murakkabroq so'zlardan foydalaning.",
            "Listening mashqlarida asosiy e'tiborni detallarga qarating.",
            "Speaking da o'z fikringizni dalillar bilan asoslashni mashq qiling."
        ],
        "B1-B2": [
            "Grammatika ustida chuqurroq ishlang (Conditionals, Passive Voice).",
            "Mavzuga oid maxsus so'zlarni (topic vocabulary) o'rganing.",
            "Writing Task 2 uchun qisqa esselar yozib, xatolarni tahlil qiling."
        ],
        "B2": [
            "IELTS Writing uchun strukturani (Introduction, Body, Conclusion) to'liq o'zlashtiring.",
            "Speaking Part 3 savollariga kengaytirilgan javob berishni mashq qiling.",
            "Akademik maqolalar (Reading) o'qib, notanish so'zlarni belgilab oling."
        ],
        "C1": [
            "Tildagi nozik ma'nolarni (idioms, phrasal verbs) joyida ishlating.",
            "Xatolaringizni o'zingiz topish va to'g'rilash ustida ishlang.",
            "Listening Part 3/4 larni diqqat bilan, chalg'ituvchi ma'lumotlarni farqlab tinglang."
        ],
        "C1-C2": [
            "Nutqingizni mutlaqo tabiiy (native-like) holatga keltiring.",
            "Juda murakkab va spesifik matnlarni osongina tahlil qila olishingiz kerak.",
            "Nuanslarni to'liq tushunishga harakat qiling."
        ],
        "C2": [
            "Siz mukammal darajadasiz! Endi faqat amaliyot bilan tilni saqlab turing.",
            "Turli dialektlar va aksentlarni tushunishni mashq qiling.",
            "Ilmiy va akademik doiralarda til imkoniyatlaridan to'liq foydalaning."
        ]
    }
    return tips.get(current_cefr, ["Mashqlarni davom ettiring va ko'proq o'qing."])
