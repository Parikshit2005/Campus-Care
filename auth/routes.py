from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Issue
import os, uuid
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)

        if user.role == 'student':
            return redirect(url_for('main.student_dashboard'))
        elif user.role == 'faculty':
            return redirect(url_for('main.faculty_dashboard'))
        elif user.role == 'authority':
            return redirect(url_for('main.authority_dashboard'))

    return render_template('auth/login.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route('/issue/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        location = request.form.get('location')
        description = request.form.get('description')
        photo = request.files.get('photo')

        photo_filename = None
        if photo and allowed_file(photo.filename):
            ext = photo.filename.rsplit('.', 1)[1].lower()
            photo_filename = f"{uuid.uuid4().hex}.{ext}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_path, exist_ok=True)
            photo.save(os.path.join(upload_path, photo_filename))

        issue = Issue(
            title=title,
            category=category,
            location=location,
            description=description,
            photo=photo_filename,
            reported_by=current_user.id
        )
        db.session.add(issue)
        db.session.commit()

        flash('Issue reported successfully.', 'success')
        return redirect(url_for('main.student_dashboard'))

    return render_template('issues/report.html')


@auth.route('/issue/update/<int:issue_id>', methods=['POST'])
@login_required
def update_issue(issue_id):
    if current_user.role != 'authority':
        flash('Unauthorized.', 'error')
        return redirect(url_for('main.index'))

    issue = Issue.query.get(issue_id)
    if not issue:
        flash('Issue not found.', 'error')
        return redirect(url_for('main.authority_dashboard'))

    status = request.form.get('status')
    assigned_to = request.form.get('assigned_to')

    if status:
        issue.status = status
    if assigned_to:
        issue.assigned_to = assigned_to
    if status == 'Resolved':
        from datetime import datetime
        issue.resolved_at = datetime.utcnow()

    db.session.commit()
    flash('Issue updated successfully.', 'success')
    return redirect(url_for('main.authority_dashboard'))

@auth.route('/issue/observe/<int:issue_id>', methods=['POST'])
@login_required
def observe_issue(issue_id):
    if current_user.role != 'faculty':
        flash('Unauthorized.', 'error')
        return redirect(url_for('main.index'))

    issue = Issue.query.get(issue_id)
    if not issue:
        flash('Issue not found.', 'error')
        return redirect(url_for('main.faculty_dashboard'))

    observation = request.form.get('observation')
    faculty_priority = request.form.get('faculty_priority')

    if observation:
        issue.faculty_observation = observation
    if faculty_priority:
        issue.faculty_priority = faculty_priority
    if faculty_priority:
        issue.priority = faculty_priority
        
    db.session.commit()
    flash('Observation submitted successfully.', 'success')
    return redirect(url_for('main.faculty_dashboard'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))