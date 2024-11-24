#database/model/control
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'  # Database URI for SQLite
app.config['SECRET_KEY'] = 'your_secret_key'  # For WTForms security
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app

# Database model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default='Low')  # Default is 'Low'

# Routes
@app.route('/')
def index():
    tasks = Task.query.all()  # Retrieve all tasks from the database
    return render_template('index.html', tasks=tasks)  # Render the index template with tasks

@app.route('/add', methods=['POST'])
def add():
    task_content = request.form['content']
    due_date = request.form['due_date']
    priority = request.form['priority']
    if task_content:
        new_task = Task(
            content=task_content,
            due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
            priority=priority
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)  # Run the app in debug mode