#database/model/control
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'  # Database URI for SQLite
app.config['SECRET_KEY'] = 'your_secret_key'  # For WTForms security
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app

# Login manager setup
login_manager = LoginManager()  # Initialize the LoginManager
login_manager.init_app(app)  # Bind the LoginManager to the Flask app
login_manager.login_view = 'login'  # Set the login view endpoint

# user DB model
class User(UserMixin, db.Model):  # Define the User model inheriting from UserMixin and db.Model
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the user
    username = db.Column(db.String(80), unique=True, nullable=False)  # Unique username field
    password = db.Column(db.String(200), nullable=False)  # Password field

@login_manager.user_loader
def load_user(user_id):  # Function to load a user by their ID
    return User.query.get(int(user_id))  # Retrieve the user from the database


# Task DB model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default='Low')  # Default is 'Low'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# main Routes
@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task_content = request.form['content']
    due_date = request.form['due_date']
    priority = request.form['priority']
    if task_content:
        new_task = Task(
            content=task_content,
            due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
            priority=priority,
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get(task_id)  # Retrieve the task by ID
    if task:  # Check if the task exists
        db.session.delete(task)  # Delete the task from the session
        db.session.commit()  # Commit the session to save changes
    return redirect(url_for('index'))  # Redirect to the index page

@app.route('/complete/<int:task_id>')
def complete(task_id):
    task = Task.query.get(task_id)  # Retrieve the task by ID
    if task:  # Check if the task exists
        task.completed = not task.completed  # Toggle the completion status
        db.session.commit()  # Commit the session to save changes
    return redirect(url_for('index'))  # Redirect to the index page

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        updated_content = request.form['content']
        if updated_content:
            task.content = updated_content
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

#login routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Attempt to hash the password
        except ValueError as e:  # Catch ValueError if the method is invalid
            return render_template('register.html', error=str(e))  # Render the register page with an error message
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)  # Run the app in debug mode