from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from .models import User
from . import db
import logging

auth = Blueprint('auth', __name__)

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(message)s')
logger = logging.getLogger("flask_app.auth")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            flash("Logged in successfully.")
            logger.debug(f"User {user.username} logged in successfully.")
            return redirect(url_for('main.index'))
        flash("Invalid username or password.")
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash("Username already exists.")
            return redirect(url_for('auth.register'))

        new_user = User(username=request.form['username'])
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        logger.debug(f"New user registered: {new_user.username}")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out.")
    return redirect(url_for('main.index'))