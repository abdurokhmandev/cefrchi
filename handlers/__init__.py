# handlers package

# Avoid executing imports at package import time that rely on a different project layout.
# Individual handler modules (start.py, speaking.py, writing.py, etc.) are imported
# explicitly where they're needed (for example in bot.py).

__all__ = [
    "start",
    "speaking",
    "writing",
    "progress",
    "vocabulary",
    "mock",
    "menu",
    "admin",
    "topics",
    "vocab",
]
