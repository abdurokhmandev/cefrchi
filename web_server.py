from aiohttp import web
from utils import db
import json
import os
from config import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD
from aiogram import Bot

bot = Bot(token=BOT_TOKEN)

# Sodda autentifikatsiya middleware
@web.middleware
async def auth_middleware(request, handler):
    # Faqat API va Admin sahifalari uchun tekshiramiz
    if request.path.startswith('/api/admin') or request.path == '/admin':
        # Cookiedan tokenni olamiz
        token = request.cookies.get('admin_token')
        if token != "authenticated_admin":
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
        response = web.json_response({"status": "ok"})
        # Cookieni domenlararo ishlashi uchun sozlaymiz
        response.set_cookie(
            'admin_token', 'authenticated_admin', 
            max_age=86400, 
            samesite='None', 
            secure=True
        )
        return response
    
    return web.HTTPFound('/login?error=1')

async def logout(request):
    response = web.HTTPFound('/login')
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
    data = await request.json()
    text = data.get('text')
    if not text: return web.json_response({"error": "No text"}, status=400)
    users = db.get_all_users()
    count = 0
    for user in users:
        try:
            await bot.send_message(user['tg_id'], text, parse_mode="HTML")
            count += 1
        except: pass
    return web.json_response({"status": "ok", "count": count})

async def topics_api(request):
    if request.method == "GET":
        topics = db.get_all_topics()
        return web.json_response([{"id": t[0], "part": t[1], "topic": t[4]} for t in topics])
    elif request.method == "POST":
        data = await request.json()
        db.add_topic(data.get('part', 1), 'ALL', 'ALL', data.get('topic'), 0)
        return web.json_response({"status": "ok"})

async def admin_page(request):
    return web.FileResponse('static/admin.html')

def create_app():
    app = web.Application(middlewares=[auth_middleware])
    
    # CORS (Vercel uchun)
    async def on_prepare(request, response):
        origin = request.headers.get('Origin')
        if origin: response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    app.on_response_prepare.append(on_prepare)

    app.router.add_get('/', lambda r: web.HTTPFound('/admin'))
    app.router.add_get('/login', login_page)
    app.router.add_post('/login', login_api)
    app.router.add_get('/logout', logout)
    app.router.add_get('/admin', admin_page)
    app.router.add_get('/api/admin/stats', get_stats)
    app.router.add_post('/api/admin/broadcast', broadcast)
    app.router.add_route('*', '/api/admin/topics', topics_api)
    app.router.add_static('/static/', path='static', name='static')
    return app

if __name__ == '__main__':
    web.run_app(create_app(), port=8080)
