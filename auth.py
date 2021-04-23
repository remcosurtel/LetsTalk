from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db, create_app
from flask_login import login_user, logout_user, login_required, current_user
import validators, re

auth = Blueprint('auth', __name__)
app = create_app()

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating if the password meets the following criteria
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    length_error = len(password) < 8
    lowercase_error = re.search(r"[a-z]", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    digit_error = re.search(r"\d", password) is None
    symbol_error = re.search(r"\W", password) is None
    
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    return {'password_ok'     : password_ok,
            'length_error'    : length_error,
            'lowercase_error' : lowercase_error,
            'uppercase_error' : uppercase_error,
            'digit_error'     : digit_error,
            'symbol_error'    : symbol_error}

'''
Displays the login page.
'''
@auth.route('/login')
def login():
    return render_template('login.html')

'''
Allows users to log in.
'''
@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        flash('Incorrect email address. Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist, reload the page
    elif not check_password_hash(user.password, password):
        flash('Incorrect password. Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the password is wrong, reload the page

    # if the above checks pass, then we know the user has the right credentials
    login_user(user, remember=remember)
    app.logger.info(f'User logged in: {user.id}')
    return redirect(url_for('main.convert'))

'''
Displays the sign up page.
'''
@auth.route('/signup')
def signup():
    return render_template('signup.html')

'''
Allows users to sign up.
Validates user input: both email and password.
'''
@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # Validate given email address
    if not validators.email(email):
        flash('Invalid email address.')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('A user with this email address already exists.')
        return redirect(url_for('auth.signup'))
    
    # Check password strength
    check = password_check(password)
    if not check['password_ok']:
        error = 'Your password is not strong enough.<br>Passwords must contain at least:'
        if check['length_error']:
            error += '<br>8 characters'
        if check['lowercase_error']:
            error += '<br>1 lowercase letter'
        if check['uppercase_error']:
            error += '<br>1 uppercase letter'
        if check['digit_error']:
            error += '<br>1 digit'
        if check['symbol_error']:
            error += '<br>1 symbol'
        flash(error)
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), admin=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    app.logger.info(f'User signed up: {new_user.id}')

    return redirect(url_for('auth.login'))

'''
Allows users to log out.
'''
@auth.route('/logout')
@login_required
def logout():
    app.logger.info(f'User logged out: {current_user.id}')
    logout_user()
    return redirect(url_for('main.index'))