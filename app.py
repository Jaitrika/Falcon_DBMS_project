from flask import Flask, render_template, request, redirect,url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'BKJN'

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="falcon"
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
         email = request.form.get('email')
         password = request.form.get('password')
 
         if not email or not password:
             flash('Email and password are required.', 'error')
             return render_template('login.html')
 
         cursor = conn.cursor(dictionary=True)
         try:
             query = "SELECT * FROM useraccount WHERE Email = %s"
             cursor.execute(query, (email,))
             user = cursor.fetchone()
 
             if user and check_password_hash(user['Password'], password):
                 session['userid'] = user['UserID']
                 session['username'] = user['Name']
                 flash('Login successful!', 'success')
                 return redirect(url_for('home'))
             else:
                 flash('Invalid email or password', 'error')
                 return render_template('login.html')
 
         except Exception as e:
             print("Login error:", e)
             flash('Something went wrong. Try again.', 'error')
             return render_template('login.html')
 
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
     if request.method == 'POST':
         name = request.form['name']
         email = request.form['email']
         phone = request.form['phone']
         password = request.form['password']
 
         hashed_password = generate_password_hash(password)
 
         cursor = conn.cursor()
         try:
             cursor.execute("""
                 INSERT INTO useraccount (Name, Email, PhoneNumber, Password, LoyaltyPoints)
                 VALUES (%s, %s, %s, %s, 0)
             """, (name, email, phone, hashed_password))
             conn.commit()
             flash("Signup successful! Please log in.")
             return redirect(url_for('login'))
         except mysql.connector.IntegrityError:
             flash("Email already exists. Try logging in.")
             return redirect(url_for('signup'))
 
     return render_template('signup.html')

@app.route('/adminLogin')
def adminLogin():
    return render_template('adminLogin.html')


@app.route('/book-flight')
def book_flight():
    return render_template('flight_booking.html')


@app.route('/submit-booking', methods=['POST'])
def submit_booking():
    flight_id = request.form['flight_id']
    passenger_name = request.form['passenger_name']

    cursor = conn.cursor()
    cursor.execute("INSERT INTO Bookings (flight_id, passenger_name) VALUES (%s, %s)", (flight_id, passenger_name))
    conn.commit()

    return redirect('/')


from models import get_all_flights

@app.route('/manage-flights')
def manage_flights():
    flights = get_all_flights()
    return render_template('flight_management.html', flights=flights)


if __name__ == '__main__':
    app.run(debug=True)
