import sqlite3
import string
import random
import os
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = 'dev_key_secret'
db_path = os.path.join(os.path.dirname(__file__), 'urls.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/', methods=('GET', 'POST'))
def index():
    short_url = None
    original_input = ""
    
    if request.method == 'POST':
        original_url = request.form.get('url')
        original_input = original_url
        
        if not original_url:
            flash('Please enter a valid URL', 'danger')
        else:
            # Basic validation to ensure http/https
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'http://' + original_url

            conn = get_db_connection()
            
            # Check if we just shortened this (optional optimization, skipping for unique generation every time or reuse)
            # We will generate a new one every time for simplicity of logic
            
            short_id = generate_short_id()
            # Ensure uniqueness
            while conn.execute('SELECT id FROM urls WHERE short_id = ?', (short_id,)).fetchone() is not None:
                short_id = generate_short_id()
            
            conn.execute('INSERT INTO urls (original_url, short_id) VALUES (?, ?)',
                         (original_url, short_id))
            conn.commit()
            conn.close()
            
            short_url = request.host_url + short_id
            flash('URL successfully shortened!', 'success')
            
    return render_template('index.html', short_url=short_url, original_input=original_input)

@app.route('/<short_id>')
def redirect_to_url(short_id):
    conn = get_db_connection()
    url_data = conn.execute('SELECT original_url FROM urls WHERE short_id = ?', (short_id,)).fetchone()
    conn.close()
    
    if url_data:
        return redirect(url_data['original_url'])
    else:
        return "<h1>404 - URL Not Found</h1><p>The link you are looking for does not exist.</p><a href='/'>Go Home</a>", 404

if __name__ == '__main__':
    if not os.path.exists(db_path):
        init_db()
    app.run(debug=True, port=5000)
