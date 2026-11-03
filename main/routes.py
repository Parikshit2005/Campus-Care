from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Issue

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('main.student_dashboard'))
        elif current_user.role == 'faculty':
            return redirect(url_for('main.faculty_dashboard'))
        elif current_user.role == 'authority':
            return redirect(url_for('main.authority_dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard/student')
@login_required
def student_dashboard():
    issues = Issue.query.filter_by(reported_by=current_user.id).order_by(Issue.created_at.desc()).all()
    return render_template('dashboards/student.html', issues=issues)

@main.route('/dashboard/faculty')
@login_required
def faculty_dashboard():
    issues = Issue.query.order_by(Issue.created_at.desc()).all()
    return render_template('dashboards/faculty.html', issues=issues)

@main.route('/dashboard/authority')
@login_required
def authority_dashboard():
    issues = Issue.query.order_by(Issue.created_at.desc()).all()
    total = Issue.query.count()
    pending = Issue.query.filter_by(status='Pending').count()
    in_progress = Issue.query.filter_by(status='In Progress').count()
    resolved = Issue.query.filter_by(status='Resolved').count()
    return render_template('dashboards/authority.html', issues=issues,
                           total=total, pending=pending,
                           in_progress=in_progress, resolved=resolved)

@main.route('/issue/<int:issue_id>')
@login_required
def issue_detail(issue_id):
    issue = Issue.query.get(issue_id)
    if not issue:
        flash('Issue not found.', 'error')
        return redirect(url_for('main.index'))
    return render_template('issues/detail.html', issue=issue)