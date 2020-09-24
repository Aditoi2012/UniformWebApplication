from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DB_NAME = "uniform.db"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'xmbcvjadsfklasfksajdf'

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None

@app.route('/')
def home():
    return render_template('home.html',logged_in=is_logged_in())

@app.route('/juniorUniform')
def juniorUniform():
    con = create_connection(DB_NAME)
    query = 'SELECT id, name, size, image, price, description FROM juniorUniform'
    cur = con.cursor()
    cur.execute(query)
    juniorProduct_list = cur.fetchall()
    con.close

    return render_template('juniorUniform.html', juniorProducts=juniorProduct_list, logged_in=is_logged_in())

@app.route('/seniorUniform')
def seniorUniform():
    con = create_connection(DB_NAME)
    query = 'SELECT id, name, size, image, price, description FROM seniorUniform'
    cur = con.cursor()
    cur.execute(query)
    seniorProduct_list = cur.fetchall()
    con.close

    return render_template('seniorUniform.html', seniorProducts=seniorProduct_list,logged_in=is_logged_in())

@app.route('/viewitem/<productid>/<uniformType>')
def viewitem(productid,uniformType):
    if uniformType == 'junioruniform':
        query = """SELECT name, size, image, price, description FROM juniorUniform WHERE id = ? """
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (productid,))
        product_data = cur.fetchall()
        # size = product_data[0][1]
        # x = ["123", "456.678", "abc.def.ghi"]
        # print(size)
        size = product_data[0][1].split(",")
        # print(size)
        # print(product_data)
        con.close()
        # print(x)
        return render_template('viewproduct.html',productData = product_data,logged_in=is_logged_in(),sizes=size,uniform=uniformType)
    else:
        query = """SELECT name, size, image, price, description FROM seniorUniform WHERE id = ? """
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (productid,))
        product_data = cur.fetchall()
        size = product_data[0][1].split(",")
        # print(size)
        # print(product_data)
        con.close()
        return render_template('viewproduct.html', productData=product_data, logged_in=is_logged_in(), sizes=size,
                               uniform=uniformType)


@app.route('/addtocart', methods=['GET','POST'])
def addtocart():
    print('yes')
    if request.method == 'POST':
        print(request.form.get('size'))
        print(request.form.get('quantity'))
        print('yes')
        return redirect(request.referrer)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect('/')

    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM customer WHERE email = ?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()

        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        session['cart'] = []
        # print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


def is_logged_in():
    if session.get("email") is None:
        # print("not logged in")
        return False
    else:
        # print("logged in")
        return True


@app.route('/signup', methods=['GET','POST'])
def signup():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        # print(request.form)
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


@app.route('/logout')
def logout():
    # print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    # print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


app.run(host='0.0.0.0', debug=True)