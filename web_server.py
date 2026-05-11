from aiohttp import web
import db
import json
import hashlib
import hmac
import urllib.parse
from config import BOT_TOKEN, ADMIN_IDS
from aiogram import Bot

bot = Bot(token=BOT_TOKEN)

@web.middleware
async def cors_middleware(request, handler):
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = web.Response(status=200)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            response = ex
        except Exception as e:
            response = web.json_response({"error": str(e)}, status=500)

    # Set CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Telegram-Init-Data, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    
    return response

def validate_init_data(init_data: str, bot_token: str):
    if not init_data:
        return False
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        if 'hash' not in parsed_data:
            return False
        
        check_hash = parsed_data.pop('hash')
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash != check_hash:
            return False
            
        user_data = json.loads(parsed_data.get('user', '{}'))
        return user_data.get('id') in ADMIN_IDS
    except:
        return False

async def get_stats(request):
    init_data = request.headers.get('X-Telegram-Init-Data')

    if not validate_init_data(init_data, BOT_TOKEN):
        return web.json_response({"error": "Unauthorized"}, status=403)
        
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
            "recent_users": all_users[:50] # Top 50 recent
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def broadcast(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    
    if not validate_init_data(init_data, BOT_TOKEN):
        return web.json_response({"error": "Unauthorized"}, status=403)
        
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
    init_data = request.headers.get('X-Telegram-Init-Data')
    
    if not validate_init_data(init_data, BOT_TOKEN):
        return web.json_response({"error": "Unauthorized"}, status=403)
        
    if request.method == "GET":
        topics = db.get_all_topics()
        # Transform rows to dicts
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

async def index(request):
    try:
        return web.FileResponse('static/admin_webapp.html')
    except:
        return web.Response(text="Admin panel frontend file not found.", status=404)

def create_app():
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get('/', index)
    app.router.add_route('*', '/api/admin/stats', get_stats)
    app.router.add_route('*', '/api/admin/broadcast', broadcast)
    app.router.add_route('*', '/api/admin/topics', topics_api)
    app.router.add_static('/static/', path='static', name='static')
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=8080)

