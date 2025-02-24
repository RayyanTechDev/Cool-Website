from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'  # Change this to something unique for your app
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Task('{self.title}')"
    
# Models
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(120))  # Tags stored as a comma-separated string
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"JournalEntry('{self.title}', '{self.date_created}')"

# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'POST':
        task_title = request.form['title']
        if task_title:
            new_task = Task(title=task_title, author=current_user)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('todo'))
    
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('todo.html', tasks=tasks)


@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author == current_user:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('todo'))


@app.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author == current_user:
        new_title = request.form['title']
        task.title = new_title
        db.session.commit()
    return redirect(url_for('todo'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pixel-art', methods=['GET', 'POST'])
@login_required
def pixel_art():
    if request.method == 'POST':
        # Here we can add functionality to save the canvas or perform other actions
        pass

    return render_template('pixel_art.html')

# Routes for the Journal
@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags = request.form['tags']  # Tags are comma-separated
        
        # Create new journal entry
        new_entry = JournalEntry(title=title, content=content, tags=tags, user_id=current_user.id)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('journal'))
    
    # Get all entries for the current user
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).all()
    return render_template('journal.html', entries=entries)

@app.route('/journal/<int:entry_id>', methods=['GET'])
@login_required
def view_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return redirect(url_for('journal'))  # Redirect if the user tries to access another user's entry
    return render_template('view_journal_entry.html', entry=entry)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_entries():
    if request.method == 'POST':
        search_term = request.form['search_term']
        entries = JournalEntry.query.filter(JournalEntry.tags.ilike(f"%{search_term}%"), JournalEntry.user_id == current_user.id).all()
        return render_template('journal.html', entries=entries)
    
    return render_template('search_entries.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        return render_template('invalidcredentials.html')  # Add error message for invalid login
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return "Username already exists!"  # You can replace this with a more elegant message
        elif existing_email:
            return "Email already in use!"  # You can replace this with a more elegant message

        # Hash password using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, email=email, password=hashed_password)

        # Add user to database
        db.session.add(user)
        db.session.commit()

        # Log the user in after signup
        login_user(user)
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        user = current_user
        user.username = new_username
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html')


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))


# Error Handlers

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


# Create database tables (first run or when model changes)
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)