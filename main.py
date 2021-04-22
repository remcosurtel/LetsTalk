from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import Currency
from app import db
from flask_login import login_required, current_user
import json, codecs

main = Blueprint('main', __name__)

def is_float(x):
    try:
        float(x)
        return True
    except:
        return False

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/convert')
@login_required
def convert():
    # Create a list of all currencies
    all_currencies = Currency.query.all()
    currencies = []
    for cur in all_currencies:
        currencies.append(cur.code)

    return render_template('convert.html', name=current_user.name, currencies=currencies, result=False, amount='Amount', cur_from='USD', cur_to='USD')

@main.route('/convert', methods=['POST'])
@login_required
def convert_post():
    amount = request.form.get('amount')
    currency_from = request.form.get('currency_from')
    currency_to = request.form.get('currency_to')

    # Check that given amount is a valid number
    if not is_float(amount):
        flash('Please enter a valid number as amount.')
        return redirect(url_for('main.convert'))
    amount = float(amount)
    if not amount > 0:
        flash('Please enter a positive real number as amount.')
        return redirect(url_for('main.convert'))
    
    # Get currency data
    cur_from = Currency.query.filter_by(code=currency_from).first()
    cur_to = Currency.query.filter_by(code=currency_to).first()
    if not cur_to or not cur_from:
        flash('Error retrieving data.')
        return redirect(url_for('main.convert'))
    
    # Calculate result
    result = amount * cur_from.usd_value / cur_to.usd_value
    result = "{:0.2f}".format(result) # Round to 2 decimal places
    
    # Create a list of all currencies
    all_currencies = Currency.query.all()
    currencies = []
    for cur in all_currencies:
        currencies.append(cur.code)

    return render_template('convert.html', name=current_user.name, currencies=currencies, result=result, amount=amount, cur_from=cur_from.code, cur_to=cur_to.code)