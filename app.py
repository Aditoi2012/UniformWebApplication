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
    query = 'SELECT id, name, size, image, price, description FROM juniorUniform WHERE type = ?;'
    cur = con.cursor()
    cur.execute(query,('junior',))
    juniorProduct_list = cur.fetchall()
    con.close

    return render_template('juniorUniform.html', juniorProducts=juniorProduct_list, logged_in=is_logged_in())

@app.route('/seniorUniform')
def seniorUniform():
    con = create_connection(DB_NAME)
    query = 'SELECT id, name, size, image, price, description FROM juniorUniform WHERE type = ?;'
    cur = con.cursor()
    cur.execute(query,('senior',))
    seniorProduct_list = cur.fetchall()
    con.close

    return render_template('seniorUniform.html', seniorProducts=seniorProduct_list,logged_in=is_logged_in())

@app.route('/viewitem/<productid>/<uniformType>')
def viewitem(productid,uniformType):
    if not is_logged_in():
        return redirect('/login')
    # if uniformType == 'junioruniform':
    query = """SELECT id, name, size, image, price, description FROM juniorUniform WHERE id = ? """
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (productid,))
    product_data = cur.fetchall()
    # size = product_data[0][1]
    # x = ["123", "456.678", "abc.def.ghi"]
    # print(size)
    size = product_data[0][2].split(",")
    # print(size)
    # print(product_data)
    con.close()
    # print(x)

    return render_template('viewproduct.html',productData = product_data,logged_in=is_logged_in(),sizes=size,uniform=uniformType)



# else:
#     query = """SELECT name, size, image, price, description FROM seniorUniform WHERE id = ? """
#     con = create_connection(DB_NAME)
#     cur = con.cursor()
#     cur.execute(query, (productid,))
#     product_data = cur.fetchall()
#     size = product_data[0][1].split(",")
#     # print(size)
#     # print(product_data)
#     con.close()
#     return render_template('viewproduct.html', productData=product_data, logged_in=is_logged_in(), sizes=size,
#                            uniform=uniformType)


@app.route('/addtocart/<productid>/<name>/<price>/<img>', methods=['GET','POST'])
def addtocart(productid,name, price,img):
    if not is_logged_in():
        return redirect('/login')
    userid = session['userid']
    timestamp = datetime.now()
    name = name
    imgsrc = img
    # print(name)
    # print(userid)
    # print(timestamp)
    if request.method == 'POST':
        try:
            productid = int(productid)
            price = int(price)
            quantity = int((request.form.get('quantity')))
        except ValueError:
            print('{} is not an integer'.format(productid))
            return redirect('/?error=Numbers+were+not+used')
        # print(price)
        # print(request.form.get('price'))
        # productId = ((request.form.get('id')))
        # print(productId)
        # print(productid)
        size = request.form.get('size')
        # print(quantity)
        if quantity == 0 or quantity >= 21:
            print('no')
            return redirect(request.referrer + "?error=Quantity+was+0")
            # need to add flash instead of this error message

        query = "INSERT INTO cart(id,userid,productid, timestamp,price,size,quantity,name,img) VALUES(NULL,?,?,?,?,?,?,?,?)"
        con = create_connection(DB_NAME)
        cur = con.cursor()

        try:
            cur.execute(query, (userid, productid, timestamp,price,size,quantity,name,imgsrc))
        except sqlite3.IntegrityError as e:
            print(e)
            print('### PROBLEM INSERTING INTO DATABASE - FOREIGN KEY ###')
            con.close()
            return redirect('/menu?error=Something+went+wrong')
        con.commit()
        con.close()


        # print(size)
        # print(request.form.get('size'))
        # print(quantity)
        # print('yes')
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
    print(userid)
    unique_product_ids = cur.fetchall()
    # product_ids = list(unique_product_ids)
    unique_product_ids = [list(i) for i in unique_product_ids]
    print(unique_product_ids)

    if len(unique_product_ids)==0:
        return redirect('/')

    # for i in range(len(unique_product_ids)):
    #     unique_product_ids[i] = unique_product_ids[i][0]
    #
    # print(unique_product_ids)

    #FUCKKKK

    # print(product_ids)
    # unique_product_ids = list(set(product_ids))
    # print(unique_product_ids)
    #
    # for i in range(len(unique_product_ids)):
    #     product_count = product_ids.count(unique_product_ids[i])
    #     unique_product_ids[i] = [unique_product_ids[i], product_count]
    # print(unique_product_ids)

    #FUCK

    # query = """SELECT price, size, name, quantity FROM cart WHERE productid =?;"""
    # for item in unique_product_ids:
    #     print(item[0])
    #     cur.execute(query, (item[0],))
    #     item_details = cur.fetchall()
    #     item.append(item_details[0][0])
    #     item.append(item_details[0][1])
    #     item.append(item_details[0][2])
    #     item.append(item_details[0][3])
    #     print(item_details)
    # con.close()
    #
    #
    # print(unique_product_ids)

    # trying to figure a way to add all the quantities

    # for i in range(len(unique_product_ids)):
    #     product_count = product_ids.count(unique_product_ids[i])
    #     unique_product_ids[i] = [unique_product_ids[i], product_count]
    # print('yes')
    # print(unique_product_ids)
    # print('no')

    # FUCK MAYBE I DONT NEED ITJFESJBK,FDSA.ADSFK.FDSAJK.

    # print(unique_product_ids[0][0][1])
    #
    # for i in range(len(unique_product_ids)):
    #     qty = unique_product_ids[i][0][2]*unique_product_ids[i][1]
    #     id_product = unique_product_ids[i][0][0]
    #     size = unique_product_ids[i][0][1]
    #     unique_product_ids[i] = [id_product,qty,size]
    #
    # print(unique_product_ids)

    # FUCK MAYBE I DONT NEED ITJFESJBK,FDSA.ADSFK.FDSAJK.

    query = """SELECT price, name,img FROM cart WHERE productid =?;"""
    for item in unique_product_ids:
        print(item[0])
        cur.execute(query, (item[0],))
        item_details = cur.fetchall()
        print(item_details)
        item.append(int(item_details[0][0]))
        item.append(item_details[0][1])
        item.append(item_details[0][2])


        print(item_details)
    con.close()

    print(unique_product_ids)

    return render_template('cart.html', cart_data=unique_product_ids, logged_in=is_logged_in())




    # trying to figure out a way to add all the quantities

    # for i in range(len(unique_product_ids)):
    #     id = unique_product_ids[i][0]
    #     qty = unique_product_ids[i][1]
    #     for q in range(len(unique_product_ids)-1):
    #         # print(id)
    #         if id == unique_product_ids[q+1][0]:
    #             totalqty = qty + unique_product_ids[q+1][1]
    #         print(unique_product_ids[i][0])




    # print(product_quantity)


    # unique_product_ids = list(set(product_ids))
    # # print(unique_product_ids)
    # for i in range(len(unique_product_ids)):
    #     product_count = product_ids.count(unique_product_ids[i])
    #     unique_product_ids[i] = [unique_product_ids[i], product_count]
    # print(product_count)
    # print(unique_product_ids)

@app.route('/removefromcart/<productid>/<quantity>/<size>/<timestamp>')
def remove_from_cart(productid,quantity,size,timestamp):
    if not is_logged_in():
        return redirect('/login')
    print('fuck')
    userid = session['userid']
    print(userid)
    print('fuck')
    print('yes')
    print(productid)
    print(quantity)
    print(size)
    # print('fuck')
    query = """DELETE FROM cart WHERE (userid, productid,timestamp, size,quantity) = (?,?,?,?,?);"""
    con = create_connection(DB_NAME)
    cur = con.cursor()
    cur.execute(query, (userid, productid,timestamp,size,quantity))
    con.commit()
    con.close()
    return redirect('/cart')

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