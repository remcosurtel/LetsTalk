from models import Currency
from app import db, create_app, config_load
import requests

if __name__ == "__main__":
    print('Updating database...')

    config = config_load()
    app = create_app()

    with app.app_context():

        # Get the current rate feed for USD
        r = requests.get(url='http://www.floatrates.com/daily/usd.json')
        data = r.json()

        # Add USD to the database if it isn't there yet
        currency = Currency.query.filter_by(code='USD').first()
        if not currency:
            new_currency = Currency(code='USD', usd_value=1)
            db.session.add(new_currency)
            db.session.commit()

        for val in data.values():
            code = val['code']
            usd_value = float(val['inverseRate'])

            # If the currency does not exist yet, create it
            currency = Currency.query.filter_by(code=code).first()
            if not currency:
                new_currency = Currency(code=code, usd_value=usd_value)
                db.session.add(new_currency)

            # Otherwise, update its value
            else:
                currency.usd_value = usd_value
            
            db.session.commit()
    
    print('Database updated.')