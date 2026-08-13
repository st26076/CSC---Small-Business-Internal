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
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_number TEXT,
                        customer_name TEXT,
                        customer_number TEXT,
                        customer_email TEXT,
                        cookie_items TEXT,
                        frosting TEXT,
                        toppings TEXT,
                        total_price REAL,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        ''')

@app.route('/')
def index():
    cookies, frostings, toppings = load_data()
    cart = session.get('cart', [])
    total_price = sum(item['price'] for item in cart)
    total_price, total_before_discount = calculate_total(cart)
    return render_template('index.html', cookies=cookies, frostings=frostings, toppings=toppings, cart=cart, total_before_discount=total_before_discount, total_price=total_price)

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
    cart = session.get('cart', [])

    if cookie not in cookies:
        flash("Invalid cookie selected - Please choose one of the following Cookie Bases")
        return redirect(url_for('index'))
    if frosting not in frostings:
        flash("Invalid frosting selected - Please choose one of the following Frosting Flavours")
        return redirect(url_for('index'))
    for topping in selected_toppings:
        if topping not in toppings:
            flash("Invalid topping selected")
            return redirect(url_for('index'))

    price_of_cookie = cookies[cookie]['price']
    price_of_cookie += frostings[frosting]['price']
    for topping in selected_toppings:
        price_of_cookie += toppings[topping]['price']

    cookie_item = {
        "cookie": cookie,
        "frosting": frosting,
        "selected_toppings": selected_toppings,
        "price": price_of_cookie
    }

    cart.append(cookie_item)
    session['cart'] = cart
    session.modified = True
    flash(f"Your Unique Cookie {cookie, frosting, selected_toppings}, has been added to cart")
    return redirect(url_for('index'))

def calculate_total(cart):
    total_before_discount = sum(cookie_item['price'] for cookie_item in cart)

    total_price = total_before_discount

    if total_price > 20:
        total_price = total_price * 0.9

    return total_price, total_before_discount

@app.route('/remove/<int:cookie_item>')
def remove(cookie_item):
    cart = session.get('cart', [])

    if 0 <= cookie_item < len(cart):
        cart.pop(cookie_item)
        session['cart'] = cart
        session.modified = True
        flash(f"Cookie removed from cart.")
    else:
        flash("Cookie not found in cart")

    return redirect(url_for('index'))


@app.route('/checkout', methods=['POST'])
def checkout():
    customer_name = request.form['customer_name'].strip().title()
    if not customer_name:
        flash("Name is required.")
        return redirect(url_for('index'))

    customer_number = request.form['customer_number'].strip()
    if not customer_number:
        flash("Phone Number is required.")
        return redirect(url_for('index'))

    customer_email = request.form['customer_email'].strip()
    if not customer_email:
        flash("Email is required.")
        return redirect(url_for('index'))

    cart = session.get('cart', [])
    if not cart:
        flash("Cart is empty")
        return redirect(url_for('index'))

    total_price, total_before_discount = calculate_total(cart)    
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    invoice_number = f"INV_NO.{customer_name.replace(' ', '_')}_{date}"

    with sqlite3.connect('unique_cookie.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO orders (invoice_number, customer_name, customer_number, customer_email, cookie_items, total_price)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (invoice_number, customer_name, customer_number, customer_email, json.dumps(cart), total_price))
            conn.commit()


    invoice_file = f"{invoice_number.replace(':', '-')}.txt"   
    try: 
        with open(invoice_file, 'w') as f:
            f.write("~ Unique Cookie Invoice ~\n\n")
            f.write(f"Invoice Number: {invoice_number}\n")
            f.write(f"Customer Name: {customer_name}\n")
            f.write(f"Customer Phone Number: {customer_number}\n")
            f.write(f"Customer Email: {customer_email}\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Cookies Ordered:\n")
            for cookie_item in cart():
                f.write(f"-{cookie_item['cookie']}: details['price']:.2f\n")
            for cookie_item in cart:
                if cookie_item['selected_toppings']:
                    f.write("\nToppings:\n")
                    for topping in cookie_item['selected_toppings']:
                        f.write(f"- {topping}\n")
            f.write(f"\nTotal: ${total_price:.2f}\n")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error writing invoice: {e}")
    return render_template('invoice.html', customer_name=customer_name, customer_number=customer_number, customer_email=customer_email, total_price=total_price, total_before_discount=total_before_discount, date=date, invoice_number=invoice_number, cart=cart, invoice_file=invoice_file)


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
    initialise_database()
    app.run(debug=True)