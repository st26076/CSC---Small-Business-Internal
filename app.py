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
    selected_toppings = session.get('selected_toppings')
    cart = session.get('cart', [])
    return render_template('index.html', cookies=cookies, frostings=frostings, toppings=toppings, selected_toppings=selected_toppings, cart=cart)

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

@app.route('/cookie_item', methods=['POST'])
def cookie_item():
    cookie = request.form['cookie']
    frosting = request.form['frosting']
    selected_toppings = request.form.getlist('toppings')
    cookies, frostings, toppings = load_data()
    cart = session.get('cart', {})

    if cookie not in cookies:
        flash("Invalid cookie selected")
        return redirect(url_for('index'))
    if frosting not in frostings:
        flash("Invalid frosting selected")
        return redirect(url_for('index'))
    if selected_toppings not in toppings:
            flash("Invalid toppings selected")
            return redirect(url_for('index'))


    total_price = cookies[cookie]['price']
    total_price += frostings[frosting]['price']
    for topping in selected_toppings:
        total_price += toppings[topping]['price']

    cookie_item = {
        "cookie": cookie,
        "frosting": frosting,
        "selected_toppings": selected_toppings,
        "price": total_price
    }

    cart.append(cookie_item)
    session['cart'] = cart
    session.modified = True
    flash(f"Your Unique Cookie, {cookie_item}, has been added to cart")
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