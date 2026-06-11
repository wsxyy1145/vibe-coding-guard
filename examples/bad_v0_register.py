"""用户注册 API —— vibe 出来先跑起来"""
import re
import sqlite3
import hashlib
import smtplib
import json
from email.mime.text import MIMEText
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            failed_login_count INTEGER DEFAULT 0,
            last_login_ip TEXT,
            role TEXT DEFAULT 'user',
            department TEXT,
            manager_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_user_by_username_or_email(conn, identifier):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? OR email=?", (identifier, identifier))
    return cur.fetchone()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def validate_password(pwd):
    if len(pwd) < 8:
        return False, "password too short"
    if not any(c.isupper() for c in pwd):
        return False, "password must contain uppercase"
    if not any(c.isdigit() for c in pwd):
        return False, "password must contain digit"
    return True, None

def send_welcome_email(to_email, username):
    msg = MIMEText(f"Welcome {username}!")
    msg['Subject'] = 'Welcome'
    msg['From'] = 'noreply@example.com'
    msg['To'] = to_email
    try:
        s = smtplib.SMTP('smtp.example.com', 25)
        s.send_message(msg)
        s.quit()
    except:
        pass

def log_audit(action, user_id, detail):
    with open('audit.log', 'a') as f:
        f.write(json.dumps({"action": action, "user_id": user_id, "detail": detail}) + '\n')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        department = data.get('department')
        manager_id = data.get('manager_id')

        if not username or not email or not password:
            return jsonify({"error": "missing fields"}), 400

        if not validate_email(email):
            return jsonify({"error": "invalid email"}), 400

        valid, msg = validate_password(password)
        if not valid:
            return jsonify({"error": msg}), 400

        salt = hashlib.sha256(str(hash(email)).encode()).hexdigest()[:16]
        pwd_hash = hash_password(password, salt)

        conn = sqlite3.connect(DB_PATH)
        try:
            existing = get_user_by_username_or_email(conn, username)
            if existing:
                conn.close()
                return jsonify({"error": "user exists"}), 409
            existing = get_user_by_username_or_email(conn, email)
            if existing:
                conn.close()
                return jsonify({"error": "user exists"}), 409

            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, email, password_hash, salt, department, manager_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, pwd_hash, salt, department, manager_id))
            conn.commit()
            user_id = cur.lastrowid
        finally:
            conn.close()

        send_welcome_email(email, username)
        log_audit("register", user_id, {"ip": request.remote_addr, "dept": department})
        return jsonify({"id": user_id, "username": username}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('username', '').strip()
    password = data.get('password', '')
    conn = sqlite3.connect(DB_PATH)
    user = get_user_by_username_or_email(conn, identifier)
    if not user:
        conn.close()
        return jsonify({"error": "not found"}), 404
    pwd_hash = hash_password(password, user[4])
    if pwd_hash != user[3]:
        conn.execute("UPDATE users SET failed_login_count = failed_login_count + 1 WHERE id=?", (user[0],))
        conn.commit()
        conn.close()
        return jsonify({"error": "wrong password"}), 401
    conn.execute("UPDATE users SET last_login_ip=?, failed_login_count=0 WHERE id=?", (request.remote_addr, user[0]))
    conn.commit()
    conn.close()
    return jsonify({"id": user[0]}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
