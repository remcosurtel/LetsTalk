# Let's Talk MVC Assignment

This application is written for an assignment by Let's Talk.

## Approach

Given my lack of experience with web development, I chose to use a language that I am comfortable with: Python.
I followed an online [tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login) for the creation of a simple web application with authentication via Flask-Login.
From there, I added further functionality step-by-step to satisfy the requirements of the assignment.
I chose to add a second dropdown menu to select a "to" currency, instead of displaying all exchange rates in a large table.
I did this because I believe it makes the tool more user friendly. As a bonus I added an admin page that allows admins to remove users and add or remove trusted IP addresses.

## Technologies used

* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [SQLite](https://www.sqlite.org/index.html)

## Getting started

In order to use the code from this repository, follow these steps:

* Install [Python](https://www.python.org/)
* Clone this repository
* Open PowerShell and change to the directory where you cloned this repository
* Execute the following commands:
```
python -m venv auth
auth/Scripts/activate
pip install -r requirements.txt
```
* Create a file named `config.json`:
```
{"secret_key": "insert_some_random_string_of_characters_here",
 "database": "sqlite:///db.sqlite",
 "trusted_ips": ["127.0.0.1"]}
```
* Create an empty file named `log.txt`
* Open a Python REPL by simply typing `python` in PowerShell and pressing enter
* Execute the following two lines to initialize the database:
```python
from app import db, create_app
db.create_all(app=create_app())
```
* Exit the Python REPL as follows:
```
quit()
```
* Run `update_db.py` to fill the database with the current currency exchange rates:
```
python update_db.py
```
* Now you can run the web application:
```
flask run
```
* Navigate to [localhost](http://localhost:5000)
* Create your account on the sign up page
* To give your account admin privileges, you can use a tool such as [SQLiteStudio](https://sqlitestudio.pl/) to modify the `admin` attribute on the user that you created
* You can now access all content on the web application

(Tested on Windows 10 using Python 3.8)