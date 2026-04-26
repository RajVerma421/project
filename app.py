from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from functools import wraps
import time
import os
import wave
from Script_generator import Script
from splitText import split_text
from tts_local import text_to_speech
from video_generator import create_dynamic_video

load_dotenv()
app = Flask(__name__)

# Database configuration
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = None
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'dev-salt-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "output", "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

rate_limit_store = {}

def rate_limit(max_requests=10, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return f(*args, **kwargs)
            
            user_id = current_user.id
            now = time.time()
            
            if user_id not in rate_limit_store:
                rate_limit_store[user_id] = []
            
            rate_limit_store[user_id] = [
                t for t in rate_limit_store[user_id]
                if now - t < window
            ]
            
            if len(rate_limit_store[user_id]) >= max_requests:
                flash('Rate limit exceeded. Please wait a moment before generating more content.', 'warning')
                return redirect(url_for('home'))
            
            rate_limit_store[user_id].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.before_request
def before_request():
    g.rate_limit = rate_limit_store

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; media-src 'self'"
    return response


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    import re
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('register'))
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.', 'danger')
            return redirect(url_for('register'))
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.', 'danger')
            return redirect(url_for('register'))
        if not re.search(r'[0-9]', password):
            flash('Password must contain at least one number.', 'danger')
            return redirect(url_for('register'))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must contain at least one special character (!@#$%^&*).', 'danger')
            return redirect(url_for('register'))
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=True)
            session.permanent = True
            
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('home'))


def validate_password(password):
    import re
    errors = []
    if len(password) < 8:
        errors.append('Password must be at least 8 characters.')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter.')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character (!@#$%^&*).')
    return errors


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.bio = request.form.get('bio')
        current_user.phone = request.form.get('phone')
        current_user.location = request.form.get('location')
        
        new_email = request.form.get('email')
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email already in use.', 'danger')
                return redirect(url_for('profile'))
            current_user.email = new_email
        
        new_password = request.form.get('new_password')
        current_password = request.form.get('current_password')
        
        if new_password:
            if not current_password:
                flash('Please enter your current password to set a new one.', 'danger')
                return redirect(url_for('profile'))
            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('profile'))
            
            errors = validate_password(new_password)
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(url_for('profile'))
            
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    current_password = request.form.get('current_password')
    
    if not current_password:
        flash('Please enter your password to delete account.', 'danger')
        return redirect(url_for('profile'))
    
    if not bcrypt.check_password_hash(current_user.password, current_password):
        flash('Password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    
    username = current_user.username
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash(f'Account "{username}" has been deleted. Sorry to see you go!', 'success')
    return redirect(url_for('home'))


@app.route('/generate_script', methods=['POST'])
@login_required
@rate_limit(max_requests=10, window=300)
def generate_script():
    topic = request.form.get('topic')
    content_type = request.form.get('type')
    emotion = request.form.get('emotion')

    if not topic or not content_type or not emotion:
        return render_template('index.html', script='Please fill in all fields.')

    if len(topic) > 200:
        return render_template('index.html', script='Topic is too long. Keep it under 200 characters.')

    try:
        script_response = Script(content_type, topic, emotion)[:300]
        
        if script_response.startswith("Sorry"):
            return render_template('index.html', script=script_response)
        
        if not script_response or not script_response.strip():
            return render_template('index.html', script='Could not generate script. Please try again.')
        
        chunks = [c.strip() for c in split_text(script_response) if c.strip()]
        
        if not chunks:
            return render_template('index.html', script='Could not generate script. Please try again.')
        
        audio_files = []
        video_filename = None

        if content_type == 'Post':
            return render_template(
                'index.html',
                script=script_response,
                audio_files=None,
                video_file=None
            )

        for i, chunk in enumerate(chunks[:3]):
            if not chunk.strip():
                continue
            filename = f"static/audio_{i}.mp3"
            audio_path = text_to_speech(chunk, filename, use_gtts=True)
            audio_files.append(audio_path)

        if not audio_files:
            return render_template('index.html', script='Could not generate audio. Please try again.')

        final_audio = "static/final_audio.mp3"
        
        try:
            from moviepy import AudioFileClip, concatenate_audioclips
            audio_clips = [AudioFileClip(f) for f in audio_files if os.path.exists(f)]
            if audio_clips:
                final_clip = concatenate_audioclips(audio_clips)
                final_clip.write_audiofile(final_audio, logger=None)
                final_clip.close()
                for clip in audio_clips:
                    clip.close()
        except Exception as e:
            print(f"Audio merge error: {e}")
            final_audio = audio_files[0]

        video_filename = None
        if content_type in ['Reel', 'YouTube Short', 'TikTok']:
            video_output = os.path.join(VIDEO_DIR, 'final_video.mp4')
            video_path = create_dynamic_video(
                script=script_response,
                audio_file=final_audio
            )
            if video_path:
                video_filename = os.path.basename(video_path)

        return render_template(
            'index.html',
            script=script_response,
            audio_files=audio_files,
            video_file=video_filename
        )

    except Exception as e:
        print('Error:', str(e))
        return render_template('index.html', script=f'Error: {str(e)}')


@app.route('/video/<path:filename>')
@login_required
def serve_video(filename):
    if '..' in filename:
        return 'Invalid filename', 400
    return send_from_directory(VIDEO_DIR, filename)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)