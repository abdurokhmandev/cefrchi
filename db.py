import sqlite3
from datetime import datetime
from config import DB_PATH

def init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users jadvali
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        tg_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        lang TEXT DEFAULT 'uz',
        level TEXT DEFAULT 'B1',
        exam TEXT DEFAULT 'IELTS',
        registered_at TEXT,
        is_blocked INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        last_activity TEXT
    )""")
    
    # Topics jadvali
    c.execute("""CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part INTEGER,
        level TEXT,
        exam TEXT,
        topic TEXT,
        category TEXT DEFAULT 'General',
        added_by INTEGER,
        created_at TEXT
    )""")
    
    # Results jadvali
    c.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        topic_id INTEGER,
        transcript TEXT,
        band TEXT,
        cefr TEXT,
        feedback TEXT,
        grammar_tips TEXT,
        vocab_tips TEXT,
        date TEXT
    )""")
    
    conn.commit()
    conn.close()

# Foydalanuvchi operatsiyalari
def add_user(tg_id, username, full_name, lang, level, exam):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR IGNORE INTO users (tg_id, username, full_name, lang, level, exam, registered_at, last_activity) VALUES (?,?,?,?,?,?,?,?)",
              (tg_id, username, full_name, lang, level, exam, date, date))
    conn.commit()
    conn.close()

def get_user(tg_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,)).fetchone()
    conn.close()
    if row:
        return {
            "tg_id": row[0], "username": row[1], "full_name": row[2],
            "lang": row[3], "level": row[4], "exam": row[5],
            "registered_at": row[6], "is_blocked": row[7],
            "streak": row[8], "last_activity": row[9]
        }
    return None

def update_streak(tg_id):
    user = get_user(tg_id)
    if not user: return
    
    now = datetime.now()
    last_act = datetime.strptime(user['last_activity'], "%Y-%m-%d %H:%M:%S") if user['last_activity'] else None
    
    conn = sqlite3.connect(DB_PATH)
    if last_act:
        diff = (now.date() - last_act.date()).days
        if diff == 1:
            conn.execute("UPDATE users SET streak = streak + 1, last_activity = ? WHERE tg_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), tg_id))
        elif diff > 1:
            conn.execute("UPDATE users SET streak = 1, last_activity = ? WHERE tg_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), tg_id))
        else:
            conn.execute("UPDATE users SET last_activity = ? WHERE tg_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), tg_id))
    else:
        conn.execute("UPDATE users SET streak = 1, last_activity = ? WHERE tg_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), tg_id))
    
    conn.commit()
    conn.close()

def update_user_field(tg_id, field, value):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"UPDATE users SET {field}=? WHERE tg_id=?", (value, tg_id))
    conn.commit()
    conn.close()

# Topik operatsiyalari
def add_topic(part, level, exam, topic, added_by, category='General'):
    conn = sqlite3.connect(DB_PATH)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO topics (part, level, exam, topic, added_by, created_at, category) VALUES (?,?,?,?,?,?,?)",
                 (part, level, exam, topic, added_by, date, category))
    conn.commit()
    conn.close()

def delete_topic(topic_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM topics WHERE id=?", (topic_id,))
    conn.commit()
    conn.close()

def get_all_topics():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM topics ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def get_filtered_topics(exam, part, level):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM topics WHERE (exam=? OR exam='ALL')"
    params = [exam]
    if part:
        query += " AND part=?"
        params.append(part)
    if level and level != 'ALL':
        query += " AND (level=? OR level='ALL')"
        params.append(level)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

# Natija operatsiyalari
def save_result(tg_id, topic_id, transcript, band, cefr, feedback, grammar="", vocab=""):
    conn = sqlite3.connect(DB_PATH)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO results (tg_id, topic_id, transcript, band, cefr, feedback, grammar_tips, vocab_tips, date) VALUES (?,?,?,?,?,?,?,?,?)",
                 (tg_id, topic_id, transcript, band, cefr, feedback, grammar, vocab, date))
    conn.commit()
    conn.close()
    update_streak(tg_id)

def get_user_results(tg_id, limit=5, offset=0):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT r.topic_id, r.band, r.cefr, r.date, t.topic, r.feedback, r.grammar_tips, r.vocab_tips
        FROM results r 
        LEFT JOIN topics t ON r.topic_id = t.id 
        WHERE r.tg_id=? 
        ORDER BY r.date DESC LIMIT ? OFFSET ?
    """, (tg_id, limit, offset)).fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_tests = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
    avg_band = conn.execute("SELECT AVG(CAST(band AS FLOAT)) FROM results WHERE band != '—'").fetchone()[0]
    conn.close()
    return total_users, total_tests, avg_band or 0

def get_daily_stats():
    conn = sqlite3.connect(DB_PATH)
    # Oxirgi 7 kundagi testlar soni
    rows = conn.execute("""
        SELECT date(date) as d, COUNT(*) 
        FROM results 
        WHERE date >= date('now', '-7 days') 
        GROUP BY d ORDER BY d ASC
    """).fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM users ORDER BY registered_at DESC").fetchall()
    conn.close()
    return rows


