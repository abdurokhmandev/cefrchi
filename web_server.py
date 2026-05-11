from aiohttp import web
import db
import json
import hashlib
import hmac
import urllib.parse
from config import BOT_TOKEN, ADMIN_IDS

def validate_init_data(init_data: str, bot_token: str):
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
    
    # CORS uchun headerlar
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Telegram-Init-Data"
    }

    if request.method == "OPTIONS":
        return web.Response(headers=headers)

    if not validate_init_data(init_data, BOT_TOKEN):
        return web.json_response({"error": "Unauthorized. Please open via Telegram Bot."}, status=403, headers=headers)
        
    try:
        total_users, total_tests, avg_band = db.get_stats()
        daily_stats = db.get_daily_stats()
        recent_users = db.get_all_users()[:20]
        
        daily_activity = [{"date": s[0], "count": s[1]} for s in daily_stats]
        users = [{"tg_id": u[0], "username": u[1], "full_name": u[2], "level": u[4], "streak": u[8]} for u in recent_users]
            
        return web.json_response({
            "total_users": total_users,
            "total_tests": total_tests,
            "avg_band": avg_band,
            "daily_activity": daily_activity,
            "recent_users": users
        }, headers=headers)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500, headers=headers)

async def broadcast(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    headers = {"Access-Control-Allow-Origin": "*"}
    
    if not validate_init_data(init_data, BOT_TOKEN):
        return web.json_response({"error": "Unauthorized"}, status=403, headers=headers)
        
    data = await request.json()
    return web.json_response({"status": "ok", "count": 0}, headers=headers)

async def index(request):
    return web.FileResponse('static/admin_webapp.html')

def create_app():

    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_route('*', '/api/admin/stats', get_stats)
    app.router.add_route('*', '/api/admin/broadcast', broadcast)
    app.router.add_static('/static/', path='static', name='static')
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=8080)
