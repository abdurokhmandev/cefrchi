from aiohttp import web, ClientSession
from utils import db
import json
import os
import asyncio
from config import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD
from aiogram import Bot

bot = Bot(token=BOT_TOKEN)

PREFIX = "/cefrchi-admin"
LOGIN_PATH = "/cefrchi_login"

# Sodda autentifikatsiya middleware
@web.middleware
async def auth_middleware(request, handler):
    # OPTIONS so'rovlari uchun darhol javob qaytaramiz (CORS Preflight)
    if request.method == 'OPTIONS':
        response = web.Response(status=200)
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Telegram-Init-Data'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Faqat API va Admin sahifalari uchun tekshiramiz
    if request.path.startswith(PREFIX + '/api/admin') or request.path == PREFIX:
        token = request.cookies.get('admin_token')
        if token != "authenticated_admin":
            if request.path.startswith(PREFIX + '/api/'):
                return web.json_response({"error": "Unauthorized"}, status=401)
            return web.HTTPFound(LOGIN_PATH)
    
    return await handler(request)

async def login_page(request):
    return web.FileResponse('static/login.html')

async def login_api(request):
    data = await request.post()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = web.json_response({"status": "ok"})
        # Cookieni domenlararo ishlashi uchun sozlaymiz
        response.set_cookie(
            'admin_token', 'authenticated_admin', 
            max_age=86400, 
            samesite='None', 
            secure=True
        )
        return response
    
    return web.HTTPFound(f'{LOGIN_PATH}?error=1')

async def logout(request):
    response = web.HTTPFound(LOGIN_PATH)
    response.del_cookie('admin_token')
    return response

async def get_stats(request):
    try:
        total_users, total_tests, avg_band = db.get_stats()
        daily_stats = db.get_daily_stats()
        all_users = db.get_all_users()
        daily_activity = [{"date": s[0], "count": s[1]} for s in daily_stats]
        return web.json_response({
            "total_users": total_users, "total_tests": total_tests,
            "avg_band": avg_band, "daily_activity": daily_activity,
            "recent_users": all_users
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def broadcast(request):
    try:
        data = await request.json()
        text = data.get('text')
        filters = data.get('filters', {})
        target_user_id = data.get('target_user_id')
        
        if not text: return web.json_response({"error": "No text"}, status=400)
        
        count = 0
        if target_user_id:
            # Faqat bitta foydalanuvchiga yuborish
            try:
                await bot.send_message(target_user_id, text, parse_mode="HTML")
                count = 1
            except Exception as e:
                return web.json_response({"error": f"Xabar yuborishda xato: {e}"}, status=400)
        else:
            # Filtrlar bo'yicha barchaga yuborish
            users = db.get_all_users()
            for user in users:
                if filters.get('exam') and user['exam'] != filters['exam']: continue
                if filters.get('level') and user['level'] != filters['level']: continue
                
                try:
                    await bot.send_message(user['tg_id'], text, parse_mode="HTML")
                    count += 1
                    await asyncio.sleep(0.05) # Telegram spamdan himoya
                except Exception as e:
                    print(f"Xato (user {user['tg_id']}): {e}")
        
        return web.json_response({"status": "ok", "count": count})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def get_user_photo(request):
    tg_id = request.match_info.get('tg_id')
    if not tg_id: return web.Response(status=400)
    
    try:
        photos = await bot.get_user_profile_photos(int(tg_id), limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id # Eng kichik o'lchamdagi rasm yetarli
            file = await bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
            
            async with ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        return web.Response(body=image_data, content_type='image/jpeg')
        
        # Rasm topilmasa yoki xato bo'lsa default rasm qaytarish yoki 404
        return web.Response(status=404)
    except Exception as e:
        print(f"Photo error: {e}")
        return web.Response(status=404)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def topics_api(request):
    if request.method == "GET":
        topics = db.get_all_topics()
        return web.json_response([
            {"id": t[0], "part": t[1], "level": t[2], "exam": t[3], "topic": t[4]} 
            for t in topics
        ])
    elif request.method == "POST":
        data = await request.json()
        topic_text = data.get('topic')
        part = data.get('part', 1)
        exam = data.get('exam', 'ALL')
        level = data.get('level', 'ALL')
        
        # 1. Bazaga saqlash
        topic_id = db.add_topic(int(part), level, exam, topic_text, 0)
        
        # 2. Userlarga xabar yuborish
        users = db.get_all_users()
        
        btn = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🎤 Sinab ko'rish", callback_data=f"start_topic_{topic_id}")
        ]])
        
        msg = f"🆕 <b>Yangi Speaking Topik!</b>\n\n🎯 {exam} | Part {part}\n📝 {topic_text[:100]}...\n\n<i>Hozirroq sinab ko'ring va AI feedback oling!</i>"
        
        for user in users:
            if exam != 'ALL' and user['exam'] != exam: continue
            if level != 'ALL' and user['level'] != level: continue
            try:
                await bot.send_message(user['tg_id'], msg, parse_mode="HTML", reply_markup=btn)
            except: pass
            
        return web.json_response({"status": "ok", "id": topic_id})

async def vocab_api(request):
    if request.method == "GET":
        exam = request.query.get('exam')
        level = request.query.get('level')
        vocabs = db.get_all_vocab(exam, level)
        return web.json_response([
            {"id": v[0], "topic": v[1], "content": v[2], "level": v[3], "exam": v[4]} 
            for v in vocabs
        ])
    elif request.method == "POST":
        data = await request.json()
        topic = data.get('topic')
        content = data.get('content')
        level = data.get('level', 'ALL')
        exam = data.get('exam', 'ALL')
        
        db.add_vocab(topic, content, level, exam)
        return web.json_response({"status": "ok"})
    elif request.method == "DELETE":
        v_id = request.query.get('id')
        if v_id:
            db.delete_vocab(int(v_id))
            return web.json_response({"status": "ok"})
        return web.json_response({"error": "Missing ID"}, status=400)

async def admin_page(request):
    return web.FileResponse('static/admin.html')

def create_app():
    app = web.Application(middlewares=[auth_middleware])
    
    # CORS (Vercel uchun)
    async def on_prepare(request, response):
        origin = request.headers.get('Origin')
        # Faqat o'zingizni domeningizni yoki barchasini (ishonchli bo'lsa) ruxsat berishingiz mumkin
        if origin: 
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Telegram-Init-Data'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    app.on_response_prepare.append(on_prepare)

    app.router.add_get('/', lambda r: web.HTTPFound(PREFIX))
    app.router.add_get(LOGIN_PATH, login_page)
    app.router.add_post(LOGIN_PATH, login_api)
    app.router.add_get(PREFIX + '/logout', logout)
    app.router.add_get(PREFIX, admin_page)
    app.router.add_route('*', PREFIX + '/api/admin/stats', get_stats)
    app.router.add_route('*', PREFIX + '/api/admin/broadcast', broadcast)
    app.router.add_route('*', PREFIX + '/api/admin/topics', topics_api)
    app.router.add_route('*', PREFIX + '/api/admin/vocab', vocab_api)
    app.router.add_get(PREFIX + '/api/admin/user-photo/{tg_id}', get_user_photo)
    app.router.add_static(PREFIX + '/static/', path='static', name='static')
    return app

if __name__ == '__main__':
    web.run_app(create_app(), port=8080)
