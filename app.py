from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DB_NAME = "uniform.db"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'a'

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/juniorUniform')
def juniorUniform():
    con = create_connection(DB_NAME)
    query = 'SELECT id, name, size, image, price, description FROM juniorUniform'
    cur = con.cursor()
    cur.execute(query)
    juniorProduct_list = cur.fetchall()
    con.close

    return render_template('juniorUniform.html', juniorProducts=juniorProduct_list)

@app.route('/seniorUniform')
def seniorUniform():
    return render_template('seniorUniform.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

app.run(host='0.0.0.0', debug=True)