import click
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Exercise, WorkoutLog
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.update(
    SECRET_KEY='changeme',
    SQLALCHEMY_DATABASE_URI='sqlite:///fitness.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command('init-db')
@click.pass_context
def init_db(ctx):
    db.create_all()
    # Admin anlegen
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('adminpass'), is_admin=True)
        db.session.add(admin)
    # Übungen anlegen
    default_exercises = ['Squat', 'Bench Press', 'Deadlift', 'Push Up', 'Pull Up']
    for name in default_exercises:
        if not Exercise.query.filter_by(name=name).first():
            db.session.add(Exercise(name=name))
    db.session.commit()
    click.echo('DB initialisiert')

# Registrierung
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Nutzername existiert', 'red')
        else:
            user = User(username=username, password=pwd)
            db.session.add(user)
            db.session.commit()
            flash('Registrierung erfolgreich', 'green')
            return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Ungültige Zugangsdaten', 'red')
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard
@app.route('/')
@login_required
def dashboard():
    exercises = Exercise.query.all()
    return render_template('dashboard.html', exercises=exercises)

# Übung hinzufügen (Admin Only)
@app.route('/exercises/add', methods=['GET', 'POST'])
@login_required
def add_exercise():
    if not current_user.is_admin:
        flash('Nur Admin kann Übungen hinzufügen', 'red')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        if name and not Exercise.query.filter_by(name=name).first():
            db.session.add(Exercise(name=name))
            db.session.commit()
            flash(f'Übung "{name}" hinzugefügt', 'green')
            return redirect(url_for('dashboard'))
        flash('Name ungültig oder existiert bereits', 'red')
    return render_template('exercise_add.html')

# Übungslog anzeigen und neu erfassen
@app.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def exercise_view(exercise_id):
    # ... bestehende Logik ...
    return render_template('exercise.html', exercise=exercise, table_logs=table_logs, chart_logs=chart_logs)

# Log bearbeiten
@app.route('/exercise/<int:exercise_id>/edit/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_log(exercise_id, log_id):
    # ... bestehende Logik ...
    return render_template('exercise_edit.html', exercise=exercise, log=log)

# Log löschen
@app.route('/exercise/<int:exercise_id>/delete/<int:log_id>', methods=['POST'])
@login_required
def delete_log(exercise_id, log_id):
    # ... bestehende Logik ...
    return redirect(url_for('exercise_view', exercise_id=exercise_id))

if __name__ == '__main__':
    app.run(debug=True)