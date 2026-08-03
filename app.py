import json
import datetime
import sqlite3
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'cookies_are_an_emotion'

def initialise_database():
    with sqlite3.connect('unique_cookie.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS orders (
                        order_id INTERGER PRIMARY KEY AUTOINCREMENT,
                        invoice_number TEXT,
                        customer_name TEXT,
                        items TEXT,
                        frosting TEXT,
                        toppings TEXT,
                        total REAL,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        ''')

@app.route('/')
def index():
    cookies, frosting, toppings = load_data()
    return render_template('index.html', cookies=cookies, frosting=frosting, toppings=toppings)

def load_data():
    try:
        with open('data/cookie.json') as file:
            cookies = json.load(file)
        with open('data/frosting.json') as file:
            frosting = json.load(file)
        with open('data/topping.json') as file:
            toppings = json.load(file)
        return cookies, frosting, toppings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
    return {}, {}, {}

    
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/order_history')
def order_history():
    return render_template('order_history.html')


@app.route('/invoice')
def invoice():
    return render_template('/invoice.html')


if __name__ == '__main__':
    app.run(debug=True)