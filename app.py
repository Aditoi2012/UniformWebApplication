from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/cart')
def cart():
    return render_template('cart.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

app.run(host='0.0.0.0', debug=True)
