from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from utils import db

class UserCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        user = db.get_user(user_id)
        
        # Adminlar har doim o'tadi
        from config import ADMIN_IDS
        if user_id in ADMIN_IDS:
            data['user'] = user
            return await handler(event, data)

        if user and user['is_blocked']:
            return # Bloklangan bo'lsa javob bermaymiz

        # Ro'yxatdan o'tmagan bo'lsa (va bu /start komandasi bo'lmasa)
        # Eslatma: /start komandasi handlers/start.py da boshqariladi, 
        # shuning uchun bu yerda faqat ma'lumotni uzatamiz.
        data['user'] = user
        return await handler(event, data)
