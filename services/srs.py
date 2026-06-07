import math
from datetime import datetime, timedelta

def calculate_next_review(quality: int, repetitions: int, ease_factor: float, interval: float) -> dict:
    """
    SuperMemo-2 (SM-2) algoritmi implementatsiyasi.
    
    quality: baho (0='Mutlaqo bilmayman', 3='Qiyin esladim', 5='Oson esladim')
    
    Qaytaradi:
    {
        "new_interval": yangi takrorlash oralig'i (kunlarda),
        "new_ease_factor": yangi qiyinlik faktori,
        "new_repetitions": yangi takrorlashlar soni,
        "next_date": keyingi takrorlash sanasi
    }
    """
    if quality < 3:
        # Xato javob bo'lsa, jarayon boshidan boshlanadi
        new_repetitions = 0
        new_interval = 1.0
        new_ease_factor = ease_factor
    else:
        if repetitions == 0:
            new_interval = 1.0
        elif repetitions == 1:
            new_interval = 6.0
        else:
            new_interval = round(interval * ease_factor)
        
        # Yangi qiyinlik faktorini hisoblash (minimum 1.3)
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)
        new_repetitions = repetitions + 1

    next_date = datetime.utcnow() + timedelta(days=new_interval)

    return {
        "new_interval": float(new_interval),
        "new_ease_factor": float(new_ease_factor),
        "new_repetitions": new_repetitions,
        "next_date": next_date
    }
