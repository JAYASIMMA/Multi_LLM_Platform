from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import ollama
import os
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'py', 'js', 'html', 'css', 'doc', 'docx'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['STATIC_FOLDER'], 'images'), exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('multi_llm.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Conversations table
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        model_name TEXT NOT NULL,
        domain TEXT NOT NULL,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        input_type TEXT,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Files table
    c.execute('''CREATE TABLE IF NOT EXISTS uploaded_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id INTEGER,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )''')
    
    # Contact submissions table
    c.execute('''CREATE TABLE IF NOT EXISTS contact_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

# Models configuration
MODELS = {
    'healthcare': {
        'name': 'Healthcare',
        'icon': '🏥',
        'models': ['Jayasimma/bharatbuddy', 'Jayasimma/Puzhavan'],
        'description': 'Medical advice, health information, and wellness guidance'
    },
    'agriculture': {
        'name': 'Agriculture',
        'icon': '🌾',
        'models': ['Jayasimma/gennai', 'Jayasimma/Puzhavan'],
        'description': 'Farming techniques, crop management, and agricultural practices'
    },
    'coding': {
        'name': 'Coding',
        'icon': '💻',
        'models': ['Jayasimma/codemium_ai', 'Jayasimma/creaton-ai'],
        'description': 'Programming help, code review, and software development'
    },
    'education': {
        'name': 'Education',
        'icon': '📚',
        'models': ['Jayasimma/Buddyllama', 'Jayasimma/creaton-ai'],
        'description': 'Learning resources, tutoring, and educational content'
    },
    'nature_medicine': {
        'name': 'Natural Medicine',
        'icon': '🌿',
        'models': ['Jayasimma/Puzhavan', 'Jayasimma/bharatbuddy'],
        'description': 'Herbal remedies, traditional medicine, and natural healing'
    },
    'tamil': {
        'name': 'Tamil Language',
        'icon': '🇮🇳',
        'models': ['conceptsintamil/tamil-llama-7b-instruct-v0.2', 'Jayasimma/Buddyllama'],
        'description': 'Tamil language support, translation, and cultural information'
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        conn = sqlite3.connect('multi_llm.db')
        c = conn.cursor()
        c.execute('INSERT INTO contact_submissions (name, email, subject, message) VALUES (?, ?, ?, ?)',
                 (name, email, subject, message))
        conn.commit()
        conn.close()
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('multi_llm.db')
        c = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                     (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('multi_llm.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('select_domain'))
        else:
            flash('Invalid credentials.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/domains')
@login_required
def select_domain():
    return render_template('domains.html', domains=MODELS)

@app.route('/select-model/<domain>')
@login_required
def select_model(domain):
    if domain not in MODELS:
        flash('Invalid domain selected.', 'danger')
        return redirect(url_for('select_domain'))
    
    return render_template('select_model.html', domain=domain, domain_info=MODELS[domain])

@app.route('/chat/<domain>/<model_name>')
@login_required
def chat(domain, model_name):
    if domain not in MODELS:
        flash('Invalid domain selected.', 'danger')
        return redirect(url_for('select_domain'))
    
    # Decode model name (replace underscores with slashes)
    model_name = model_name.replace('_', '/')
    
    return render_template('chat.html', domain=domain, model_name=model_name, domain_info=MODELS[domain])

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.json
    model_name = data.get('model')
    user_message = data.get('message')
    conversation_id = data.get('conversation_id')
    domain = data.get('domain')
    
    conn = sqlite3.connect('multi_llm.db')
    c = conn.cursor()
    
    # Create new conversation if needed
    if not conversation_id:
        # Create title from first message
        title = user_message[:50] + '...' if len(user_message) > 50 else user_message
        c.execute('INSERT INTO conversations (user_id, model_name, domain, title) VALUES (?, ?, ?, ?)',
                 (session['user_id'], model_name, domain, title))
        conversation_id = c.lastrowid
    
    # Save user message
    c.execute('INSERT INTO messages (conversation_id, user_id, role, content, input_type) VALUES (?, ?, ?, ?, ?)',
             (conversation_id, session['user_id'], 'user', user_message, 'text'))
    
    try:
        # Get AI response from Ollama
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': user_message}],
            stream=False
        )
        
        ai_response = response['message']['content']
        
        # Save AI response
        c.execute('INSERT INTO messages (conversation_id, user_id, role, content, input_type) VALUES (?, ?, ?, ?, ?)',
                 (conversation_id, session['user_id'], 'assistant', ai_response, 'text'))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'conversation_id': conversation_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    finally:
        conn.close()

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    conversation_id = request.form.get('conversation_id')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{session['user_id']}_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        conn = sqlite3.connect('multi_llm.db')
        c = conn.cursor()
        c.execute('INSERT INTO uploaded_files (user_id, conversation_id, filename, file_path, file_type) VALUES (?, ?, ?, ?, ?)',
                 (session['user_id'], conversation_id, file.filename, filepath, file.filename.rsplit('.', 1)[1].lower()))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'filepath': filepath, 'filename': filename})
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/history')
@login_required
def history():
    conn = sqlite3.connect('multi_llm.db')
    c = conn.cursor()
    c.execute('''SELECT c.id, c.model_name, c.domain, c.title, c.created_at, 
                 COUNT(m.id) as message_count
                 FROM conversations c
                 LEFT JOIN messages m ON c.id = m.conversation_id
                 WHERE c.user_id = ?
                 GROUP BY c.id
                 ORDER BY c.created_at DESC''', (session['user_id'],))
    conversations = c.fetchall()
    conn.close()
    
    return render_template('history.html', conversations=conversations)

@app.route('/conversation/<int:conversation_id>')
@login_required
def view_conversation(conversation_id):
    conn = sqlite3.connect('multi_llm.db')
    c = conn.cursor()
    
    # Get conversation details
    c.execute('SELECT * FROM conversations WHERE id = ? AND user_id = ?', 
             (conversation_id, session['user_id']))
    conversation = c.fetchone()
    
    if not conversation:
        flash('Conversation not found.', 'danger')
        return redirect(url_for('history'))
    
    # Get all messages
    c.execute('SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC',
             (conversation_id,))
    messages = c.fetchall()
    conn.close()
    
    return render_template('view_conversation.html', conversation=conversation, messages=messages)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)