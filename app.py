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
    cookies, frostings, toppings = load_data()
    return render_template('index.html', cookies=cookies, frostings=frostings, toppings=toppings)

def load_data():
    try:
        with open('data/cookie.json') as file:
            cookies = json.load(file)
        with open('data/frosting.json') as file:
            frosting = json.load(file)
        with open('data/toppings.json') as file:
            toppings = json.load(file)
        return cookies, frosting, toppings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
    return {}, {}, {}

@app.route('/cookie_to_cart', methods=['POST'])
def cookie_to_cart():
    cookie = request.form['cookie']
    cookies, _, _ = load_data
    cart = session.get('cart', {})

    if cookie not in cookies:
        flash("Invalid cookie selected")
        return redirect(url_for('index'))

    if cookie in cart:
        cart[cookie]

    else:
        cart[cookie] = {
            'price': cookies[cookie]['price']
        }

    session['cart'] = cart
    session.modified = True
    flash(f"{cookie} added to cart")
    return redirect(url_for('index'))


@app.route('/frosting_to_cart', methods=['POST'])
def frosting_to_cart():
    frosting = request.form['frosting']
    _, frostings, _ = load_data
    cart = session.get('cart', {})

    if frosting not in frostings:
        flash("Invalid frosting selected")
        return redirect(url_for('index'))

    if frosting in cart:
        cart[frosting]

    else:
        cart[frosting] = {
            'price': frostings[frosting]['price']
        }

    session['cart'] = cart
    session.modified = True
    flash(f"{frosting} added to cart")
    return redirect(url_for('index'))

@app.route('/toppings_to_cart', methods=['POST'])
def toppings_to_cart():
    toppings_to_cart = {}
    toppings = load_data()

    selected_keys = request.form.getlist('toppings')

    for topping in selected_keys:
        if topping in toppings:
            toppings_to_cart[topping] = {
                'price': toppings[topping]['price']
            }

    if not selected_keys:
            flash("Invalid toppings selected")
            return redirect(url_for('index'))

    if topping in toppings_to_cart:
            toppings_to_cart[topping]

    else: toppings_to_cart[topping] = {
            'price': toppings[topping]['price']
        }

    session['toppings_to_cart'] = toppings_to_cart
    session.modified = True
    flash(f"{topping}(s) added to cart")
    return redirect(url_for('index'))

    
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