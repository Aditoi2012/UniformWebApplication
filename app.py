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
    con = create_connection(DB_NAME)
    query = 'SELECT id, name, size, image, price, description FROM seniorUniform'
    cur = con.cursor()
    cur.execute(query)
    seniorProduct_list = cur.fetchall()
    con.close

    return render_template('seniorUniform.html', seniorProducts=seniorProduct_list)

@app.route('/cart')
def cart():
    return render_template('cart.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    # if is_logged_in():
    #     return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DB_NAME)
        query = "INSERT INTO customer(id, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # You need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))  # this line actually executes the query
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+is+already+used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html')

app.run(host='0.0.0.0', debug=True)