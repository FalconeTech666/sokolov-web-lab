from flask import Blueprint, render_template, session, redirect, url_for, request
from functools import wraps
from models import User

api_docs_bp = Blueprint('api_docs_bp', __name__, url_prefix='/api')

def get_current_user():
    login = session.get('user_login')
    if login:
        return User.query.filter_by(login=login).first()
    return None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped

@api_docs_bp.route('/')
@login_required
def api_index():
    return render_template('api_index.html', user=get_current_user())

@api_docs_bp.route('/tasks/')
@login_required
def api_tasks():
    return render_template('api_tasks.html', user=get_current_user())

@api_docs_bp.route('/reminders/')
@login_required
def api_reminders():
    return render_template('api_reminders.html', user=get_current_user())

@api_docs_bp.route('/validator/')
@login_required
def api_validator():
    return render_template('api_validator.html', user=get_current_user())

@api_docs_bp.route('/news/')
@login_required
def api_news():
    return render_template('api_news.html', user=get_current_user())