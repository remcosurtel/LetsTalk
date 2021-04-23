from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import User, Currency
from app import db, config_load, create_app
from flask_login import login_required, current_user
import validators, json

main = Blueprint('main', __name__)
app = create_app()

def is_float(x):
    try:
        float(x)
        return True
    except:
        return False

def is_int(x):
    try:
        int(x)
        return True
    except:
        return False

@main.route('/')
def index():
    return render_template('index.html')

'''
Displays the convert page.
'''
@main.route('/convert')
@login_required
def convert():
    # Create a list of all currencies
    all_currencies = Currency.query.all()
    currencies = []
    for cur in all_currencies:
        currencies.append(cur.code)

    return render_template('convert.html', currencies=currencies, result=False, amount='Amount', cur_from='USD', cur_to='USD')

'''
Converts a given amount of some currency to another currency.
All conversions are performed by first converting to USD.
In this way, only 1 value needs to be stored for each currency.
'''
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

    return render_template('convert.html', currencies=currencies, result=result, amount=amount, cur_from=cur_from.code, cur_to=cur_to.code)

'''
Displays the admin page.
'''
@main.route('/admin')
@login_required
def admin():
    # If user is not an admin, redirect to homepage
    if not current_user.admin:
        return redirect(url_for('main.index'))
    
    return render_template('admin.html')

'''
Lets admins remove a user by their ID.
'''
@main.route('/admin_remove_user', methods=['POST'])
@login_required
def remove_user():
    # If user is not an admin, redirect to homepage
    if not current_user.admin:
        return redirect(url_for('main.index'))
    
    user_id = request.form.get('user')
    if not is_int(user_id):
        flash('Invalid user ID.')
        return redirect(url_for('main.admin'))
    user_id = int(user_id)
    
    user = User.query.filter_by(id=user_id).first()

    if not user:
        flash('User does not exist.')
        return redirect(url_for('main.admin'))
    
    if user.admin:
        flash('You cannot remove other admins.')
        return redirect(url_for('main.admin'))
    
    user.delete()
    db.session.commit()

    app.logger.info(f'Admin {current_user.id} removed user: {user_id}')

    return render_template('admin.html', removed_user=user_id)

'''
Lets admins add/remove trusted IP addresses.
'''
@main.route('/admin_toggle_ip', methods=['POST'])
@login_required
def toggle_ip():
    # If user is not an admin, redirect to homepage
    if not current_user.admin:
        return redirect(url_for('main.index'))
    
    ip_address = request.form.get('ip')

    if not validators.ip_address.ipv4(ip_address) and not validators.ip_address.ipv6(ip_address):
        flash('Invalid IP address.')
        return redirect(url_for('main.admin'))
    
    config = config_load()

    added = True
    if ip_address in config['trusted_ips']:
        config['trusted_ips'].remove(ip_address)
        added = False
    else:
        config['trusted_ips'].append(ip_address)
    
    with open('config.json', 'w', encoding='utf-8') as doc:
        json.dump(config, doc, ensure_ascii=False, indent=4)
    
    if added:
        app.logger.info(f'Admin {current_user.id} added trusted IP: {ip_address}')
        return render_template('admin.html', removed_ip=False, added_ip=True, ip=ip_address)
    else:
        app.logger.info(f'Admin {current_user.id} removed trusted IP: {ip_address}')
        return render_template('admin.html', removed_ip=True, added_ip=False, ip=ip_address)