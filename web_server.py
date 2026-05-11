from aiohttp import web
from utils import db
import json
import os
import base64
from config import BOT_TOKEN, ADMIN_IDS, ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY
from aiogram import Bot
import aiohttp_session
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

bot = Bot(token=BOT_TOKEN)

# Middleware for authentication check
@web.middleware
async def auth_middleware(request, handler):
    # API va Admin sahifalari uchun tekshiruv
    if request.path.startswith('/api/admin') or request.path == '/admin':
        session = await get_session(request)
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                return web.json_response({"error": "Unauthorized"}, status=401)
            return web.HTTPFound('/login')
    
    return await handler(request)

async def login_page(request):
    return web.FileResponse('static/login.html')

async def login_api(request):
    data = await request.post()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session = await get_session(request)
        session['logged_in'] = True
        return web.HTTPFound('/admin')
    
    return web.HTTPFound('/login?error=1')

async def logout(request):
    session = await get_session(request)
    session.clear()
    return web.HTTPFound('/login')

async def get_stats(request):
    try:
        total_users, total_tests, avg_band = db.get_stats()
        daily_stats = db.get_daily_stats()
        all_users = db.get_all_users()
        
        daily_activity = [{"date": s[0], "count": s[1]} for s in daily_stats]
        
        return web.json_response({
            "total_users": total_users,
            "total_tests": total_tests,
            "avg_band": avg_band,
            "daily_activity": daily_activity,
            "recent_users": all_users # Full list for CRM
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def broadcast(request):
    data = await request.json()
    text = data.get('text')
    if not text:
        return web.json_response({"error": "No text provided"}, status=400)

    users = db.get_all_users()
    count = 0
    for user in users:
        try:
            await bot.send_message(user['tg_id'], text, parse_mode="HTML")
            count += 1
        except:
            pass
            
    return web.json_response({"status": "ok", "count": count})

async def topics_api(request):
    if request.method == "GET":
        topics = db.get_all_topics()
        topics_list = [{"id": t[0], "part": t[1], "level": t[2], "exam": t[3], "topic": t[4]} for t in topics]
        return web.json_response(topics_list)
    
    elif request.method == "POST":
        data = await request.json()
        topic = data.get('topic')
        part = data.get('part', 1)
        if not topic:
            return web.json_response({"error": "No topic provided"}, status=400)
        
        db.add_topic(part, 'ALL', 'ALL', topic, 0)
        return web.json_response({"status": "ok"})

async def admin_page(request):
    return web.FileResponse('static/admin.html')

def create_app():
    # Fernet key generate (must be 32 url-safe base64-encoded bytes)
    # We use our SECRET_KEY and pad/truncate it
    key = base64.urlsafe_b64encode(SECRET_KEY.encode()[:32].ljust(32, b'-'))
    
    app = web.Application(middlewares=[
        session_middleware(EncryptedCookieStorage(key)),
        auth_middleware
    ])
    
    app.router.add_get('/', lambda r: web.HTTPFound('/admin'))
    app.router.add_get('/login', login_page)
    app.router.add_post('/login', login_api)
    app.router.add_get('/logout', logout)
    app.router.add_get('/admin', admin_page)
    
    # APIs
    app.router.add_get('/api/admin/stats', get_stats)
    app.router.add_post('/api/admin/broadcast', broadcast)
    app.router.add_route('*', '/api/admin/topics', topics_api)
    
    app.router.add_static('/static/', path='static', name='static')
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=8080)
