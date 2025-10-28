from flask import Flask, request, send_from_directory, jsonify
import os
import json
import re
import hashlib
from datetime import datetime

app = Flask(__name__, static_folder='')
REG_FILE = os.path.join(os.path.dirname(__file__), 'registros.jsonl')
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.jsonl')

# Ensure file exists
open(REG_FILE, 'a').close()
open(USERS_FILE, 'a').close()


def _read_jsonl(path):
    items = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    # skip malformed lines
                    continue
    except FileNotFoundError:
        pass
    return items


def email_exists(email: str) -> bool:
    email = (email or '').strip().lower()
    if not email:
        return False
    users = _read_jsonl(USERS_FILE)
    for u in users:
        if u.get('email', '').strip().lower() == email:
            return True
    return False


def password_valid(password: str):
    if not isinstance(password, str):
        return False, 'password-missing'
    if len(password) < 8:
        return False, 'min-length-8'
    if not re.search(r'[A-Z]', password):
        return False, 'missing-uppercase'
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, 'missing-symbol'
    return True, ''


def hash_password(password: str) -> str:
    # simple sha256 hash for example purposes (do NOT use in production without salt/pepper)
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify(ok=False, error='invalid-json'), 400
        entry = {'receivedAt': datetime.utcnow().isoformat() + 'Z'}
        entry.update(data)
        with open(REG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify(ok=False, error='invalid-json'), 400
        # require some fields: name, surname, email, password
        name = (data.get('name') or '').strip()
        surname = (data.get('surname') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password')

        if not name or not surname:
            return jsonify(ok=False, error='missing-name-or-surname'), 400
        if not email:
            return jsonify(ok=False, error='missing-email'), 400
        if email_exists(email):
            return jsonify(ok=False, error='email-exists'), 409

        valid, reason = password_valid(password)
        if not valid:
            return jsonify(ok=False, error='weak-password', reason=reason), 400

        # persist user (store a basic user record without plaintext password)
        user_record = {
            'email': email,
            'name': name,
            'surname': surname,
            'passwordHash': hash_password(password),
            'createdAt': datetime.utcnow().isoformat() + 'Z'
        }
        with open(USERS_FILE, 'a', encoding='utf-8') as uf:
            uf.write(json.dumps(user_record, ensure_ascii=False) + '\n')

        # also record registration event in registros
        entry = {'type': 'register', 'receivedAt': datetime.utcnow().isoformat() + 'Z'}
        entry.update({'user': {'email': email, 'name': name, 'surname': surname}})
        with open(REG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify(ok=False, error='invalid-json'), 400
        entry = {'type': 'checkout', 'receivedAt': datetime.utcnow().isoformat() + 'Z'}
        entry.update(data)
        with open(REG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/users', methods=['GET'])
def list_users():
    try:
        users = _read_jsonl(USERS_FILE)
        # do not expose passwordHash
        safe = [{'email': u.get('email'), 'name': u.get('name'), 'surname': u.get('surname'), 'createdAt': u.get('createdAt')} for u in users]
        return jsonify(ok=True, users=safe)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/bulk', methods=['POST'])
def bulk_upload():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify(ok=False, error='expected-list'), 400
        written = 0
        with open(REG_FILE, 'a', encoding='utf-8') as f:
            for item in data:
                if not isinstance(item, dict):
                    continue
                record = {'receivedAt': datetime.utcnow().isoformat() + 'Z'}
                record.update(item)
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                written += 1
        return jsonify(ok=True, written=written)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.route('/', defaults={'path': 'prueba2.html'})
@app.route('/<path:path>')
def static_proxy(path):
    # serve static files from project root
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
