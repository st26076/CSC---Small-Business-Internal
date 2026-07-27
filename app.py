import json
import datetime
import sqlite3
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'cookies_are_an_emotion'

@app.route('/')
def index():

    return render_template('index.html')


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