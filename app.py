from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

DB_NAME = "uniform.db"

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'xmbcvjadsfklasfksajdf'

def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
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
    query = 'SELECT id, name, size, image, price, description FROM products WHERE type = ?;'
    cur = con.cursor()
    cur.execute(query,('junior',))
    juniorProduct_list = cur.fetchall()
    con.close

    return render_template('juniorUniform.html', juniorProducts=juniorProduct_list, logged_in=is_logged_in())

@app.route('/seniorUniform')
def seniorUniform():
    con = create_connection(DB_NAME)
    query = 'SELECT id, name, size, image, price, description FROM products WHERE type = ?;'
    cur = con.cursor()
    cur.execute(query,('senior',))
    seniorProduct_list = cur.fetchall()
    con.close

    return render_template('seniorUniform.html', seniorProducts=seniorProduct_list,logged_in=is_logged_in())

@app.route('/viewitem/<productid>/<uniform>')
def viewitem(productid,uniform):
    if not is_logged_in():
        return redirect('/login')
    query = """SELECT id, name, size, image, price, description,type FROM products WHERE id = ? """
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (productid,))


    product_data = cur.fetchall()

    try:
        size = product_data[0][2].split(",")
    except IndexError:
        return redirect("/?error=Item+nonexistent")

    con.close()

    return render_template('viewproduct.html',productData = product_data,logged_in=is_logged_in(),sizes=size,uniformType = uniform)


@app.route('/addtocart/<productid>', methods=['GET','POST'])
def addtocart(productid):
    if not is_logged_in():
        return redirect('/login')
    userid = session['userid']
    timestamp = str(datetime.now())
    timestamp = timestamp.replace(' ', '-')

    if request.method == 'POST':
        try:
            productid = int(productid)
            quantity = int((request.form.get('quantity')))

        except ValueError:
            return redirect(request.referrer + "?error=Numbers+were+not+used")

        size = request.form.get('size')

        if quantity == 0 or quantity >= 21:
            return redirect(request.referrer + "?error=Quantity+was+0+or+greater+than+20")


        query = "INSERT INTO cart(id,userid,productid, timestamp,size,quantity) VALUES(NULL,?,?,?,?,?)"
        con = create_connection(DB_NAME)
        cur = con.cursor()

        try:
            cur.execute(query, (userid, productid, timestamp,size,quantity))
        except sqlite3.IntegrityError as e:
            con.close()
            return redirect('/?error=Something+went+wrong')
        con.commit()
        con.close()
        return redirect(request.referrer)

@app.route('/cart')
def render_cart():
    if not is_logged_in():
        return redirect('/login')
    userid = session['userid']
    query = "SELECT productid, size, quantity,timestamp FROM cart WHERE userid=?;"
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (userid,))
    product_ids = cur.fetchall()
    product_ids = [list(i) for i in product_ids]
    if len(product_ids)==0:
        return redirect('/?error=No+items+in+cart')
    product_ids[0][3] = product_ids[0][3].replace(' ','-')

    query = """SELECT price, name,image FROM products WHERE id =?;"""
    for item in product_ids:
        cur.execute(query, (item[0],))
        item_details = cur.fetchall()
        item.append(int(item_details[0][0]))
        item.append(item_details[0][1])
        item.append(item_details[0][2])


    con.close()


    return render_template('cart.html', cart_data=product_ids, logged_in=is_logged_in())

@app.route('/removefromcart/<productid>/<quantity>/<size>/<timestamp>')
def remove_from_cart(productid,quantity,size,timestamp):
    if not is_logged_in():
        return redirect('/login')
    userid = session['userid']
    query = """DELETE FROM cart WHERE (userid, productid,timestamp, size,quantity) = (?,?,?,?,?);"""
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (userid, productid,timestamp,size,quantity))
    con.commit()
    con.close()
    return redirect('/cart')

@app.route('/login', methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect('/')

    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT userid, fname, password FROM customer WHERE email = ?"""
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
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


def is_logged_in():
    if session.get("email") is None:
        return False
    else:
        return True


@app.route('/signup', methods=['GET','POST'])
def signup():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
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
        query = "INSERT INTO customer(userid, fname, lname, email, password) " \
                "VALUES(NULL,?,?,?,?)"

        cur = con.cursor()  # You need this line next
        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('/signup?error=Email+is+already+used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    return redirect('/?message=See+you+next+time!')


app.run(host='0.0.0.0', debug=True)