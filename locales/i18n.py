import json
import os

class I18n:
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = locales_dir
        self.translations = {}
        # Ensure dir exists before trying to load
        os.makedirs(self.locales_dir, exist_ok=True)
        self._load_translations()

    def _load_translations(self):
        for lang in ['uz', 'ru', 'en']:
            file_path = os.path.join(self.locales_dir, f"{lang}.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
            else:
                self.translations[lang] = {}

    def get(self, key: str, lang: str = 'uz', **kwargs) -> str:
        """Tarjima matnini olish va formatlash"""
        text = self.translations.get(lang, {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

# Global obyekt
i18n = I18n(locales_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales"))
