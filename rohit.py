from flask import Flask, request, send_from_directory, jsonify, render_template_string, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key")  # Use env var in production

# Hardcoded users (you can switch to a database later)
USERS = {
    "admin": "password123",
    "yam": "mypassword"
}

# Folder for uploaded files
UPLOAD_FOLDER = "cloud_storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx", "xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------- HTML Templates --------------------
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Cloud Server</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 10px; width: 300px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { text-align: center; }
        input, button { margin: 10px 0; padding: 10px; width: 100%; border-radius: 5px; border: 1px solid #ccc; }
        button { background: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 Login</h2>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Cloud Server</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 10px; width: 400px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        input[type=file], button { margin: 10px 0; padding: 10px; width: 100%; border-radius: 5px; border: 1px solid #ccc; }
        button { background: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background: #45a049; }
        a { text-decoration: none; color: #007BFF; }
        .logout { float: right; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>☁️ Python Cloud Server</h2>
        <p>Welcome, {{ user }} <a href="/logout" class="logout">🚪 Logout</a></p>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload File</button>
        </form>
        <h3>📂 Files</h3>
        <ul>
            {% for file in files %}
            <li><a href="/download/{{ file }}">{{ file }}</a></li>
            {% else %}
            <li>No files uploaded yet.</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""


# -------------------- Routes --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username'].strip()
        pwd = request.form['password'].strip()
        if user in USERS and USERS[user] == pwd:
            session['user'] = user
            return redirect(url_for('home'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="❌ Invalid username or password")
    return render_template_string(LOGIN_TEMPLATE, error=None)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(HOME_TEMPLATE, files=files, user=session['user'])


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('home'))
    else:
        return "❌ File type not allowed", 400


@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/files', methods=['GET'])
def list_files():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify({"files": files})


# -------------------- Run App --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
