from flask import Flask, render_template, request, redirect, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "foodsecretkey"
conn = mysql.connector.connect(
    host="fooddb.chgm88ukgqfq.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="Himajoy123*",
    database="fooddb"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = conn.cursor()

        query = """
        INSERT INTO users(username,email,password)
        VALUES(%s,%s,%s)
        """

        values = (username,email,hashed_password)

        cursor.execute(query, values)

        conn.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = conn.cursor(dictionary=True, buffered=True)

        query = "SELECT * FROM users WHERE email=%s"

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user:

            stored_password = user['password'].encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_password):

                session['user'] = user['username']

                return redirect('/dashboard')
    return render_template('login.html')    

@app.route('/dashboard')
def dashboard():

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM foods")

    foods = cursor.fetchall()

    return render_template('dashboard.html', foods=foods)

@app.route('/addfood', methods=['GET','POST'])
def addfood():

    if request.method == 'POST':

        food_name = request.form['food_name']
        price = request.form['price']

        cursor = conn.cursor()

        query = """
        INSERT INTO foods(food_name,price)
        VALUES(%s,%s)
        """

        cursor.execute(query, (food_name,price))

        conn.commit()

        return redirect('/dashboard')

    return render_template('admin.html')

@app.route('/deletefood/<int:id>')
def deletefood(id):

    cursor = conn.cursor()

    query = "DELETE FROM foods WHERE id=%s"

    cursor.execute(query, (id,))

    conn.commit()

    return redirect('/dashboard')    

@app.route('/editfood/<int:id>', methods=['GET','POST'])
def editfood(id):

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        food_name = request.form['food_name']
        price = request.form['price']

        query = """
        UPDATE foods
        SET food_name=%s, price=%s
        WHERE id=%s
        """

        cursor.execute(query, (food_name,price,id))

        conn.commit()

        return redirect('/dashboard')

    query = "SELECT * FROM foods WHERE id=%s"

    cursor.execute(query, (id,))

    food = cursor.fetchone()

    return render_template('editfood.html', food=food)

@app.route('/cart/<int:id>')
def cart(id):

    cursor = conn.cursor()

    query = """
    INSERT INTO cart(food_id,quantity)
    VALUES(%s,%s)
    """

    cursor.execute(query, (id,1))

    conn.commit()

    return redirect('/viewcart')

@app.route('/viewcart')
def viewcart():

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT cart.id, foods.food_name, foods.price
    FROM cart
    JOIN foods
    ON cart.food_id = foods.id
    """

    cursor.execute(query)

    cartitems = cursor.fetchall()

    return render_template('cart.html', cartitems=cartitems)

@app.route('/placeorder')
def placeorder():

    cursor = conn.cursor()

    query = """
    INSERT INTO orders(user_id,food_id,quantity)
    SELECT 1, food_id, quantity FROM cart
    """

    cursor.execute(query)

    conn.commit()

    cursor.execute("DELETE FROM cart")

    conn.commit()

    return "Order Placed Successfully"

@app.route('/orders')
def orders():

    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT orders.id, foods.food_name, foods.price
    FROM orders
    JOIN foods
    ON orders.food_id = foods.id
    """

    cursor.execute(query)

    orderitems = cursor.fetchall()

    return render_template('orders.html', orderitems=orderitems)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)