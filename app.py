from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_all_flights

app = Flask(__name__)
app.secret_key = 'BKJN'

# MySQL connection
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="hi!",
    database="FLIGHTSYSTEM"
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


@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        admin_id = request.form.get('admin_id')

        if not email or not admin_id:
            flash('Email and Admin ID are required.', 'error')
            return render_template('adminLogin.html')

        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM admin WHERE Email = %s"
            cursor.execute(query, (email,))
            admin = cursor.fetchone()

            if admin and admin['AdminID'] == int(admin_id):
                session['admin_id'] = admin['AdminID']
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_home'))
            else:
                flash('Invalid email or admin ID', 'error')
                return render_template('adminLogin.html')

        except Exception as e:
            print("Admin login error:", e)
            flash('Something went wrong. Try again.', 'error')
            return render_template('adminLogin.html')

    return render_template('adminLogin.html')


@app.route('/admin-home')
def admin_home():
    if 'admin_id' not in session:
        flash("Access denied. Please log in as admin.", "error")
        return redirect(url_for('admin_login'))
    return render_template('admin_home.html')


@app.route('/booking-details', methods=['GET'])
def booking_details():
    if 'admin_id' not in session:
        flash("Access denied. Please log in as admin.", "error")
        return redirect(url_for('admin_login'))

    action = request.args.get('action')
    user_id = request.args.get('user_id')
    flight_id = request.args.get('flight_id')

    cursor = conn.cursor(dictionary=True)
    results = {
        'bookings_user': [],
        'tickets_flight': [],
        'payments_user': [],
        'requests_flight': []
    }

    try:
        if action == 'user_bookings' and user_id:
            cursor.execute("""
                SELECT B.BookingID, B.FlightID, F.AirlineName, F.FlightNumber, 
                       F.Source, F.Destination, F.DepartureTime, B.Status AS BookingStatus
                FROM Booking B
                JOIN Flight F ON B.FlightID = F.FlightID
                WHERE B.UserID = %s
            """, (user_id,))
            results['bookings_user'] = cursor.fetchall()

        elif action == 'flight_tickets' and flight_id:
            cursor.execute("""
                SELECT P.UserID, U.Name AS PassengerName, T.TicketID, 
                       T.BookingID, T.PassengerID
                FROM Ticket T
                JOIN Booking B ON T.BookingID = B.BookingID
                JOIN Passenger P ON T.PassengerID = P.PassengerID
                JOIN UserAccount U ON P.UserID = U.UserID
                WHERE B.FlightID = %s
            """, (flight_id,))
            results['tickets_flight'] = cursor.fetchall()

        elif action == 'payment_status' and user_id:
            cursor.execute("""
                SELECT B.BookingID, B.FlightID, F.AirlineName, F.FlightNumber,
                       F.Source, F.Destination, F.DepartureTime, B.Status AS BookingStatus,
                       P.PaymentID, P.AmountPaid, P.PaymentMethod, P.PaymentStatus
                FROM Booking B
                LEFT JOIN Payments P ON B.BookingID = P.BookingID
                JOIN Flight F ON B.FlightID = F.FlightID
                WHERE B.UserID = %s
            """, (user_id,))
            results['payments_user'] = cursor.fetchall()

        elif action == 'special_requests' and flight_id:
            cursor.execute("""
                SELECT SR.RequestID, B.BookingID, SR.RequestDetails, SR.Status
                FROM SpecialRequests SR
                JOIN Ticket T ON SR.TicketID = T.TicketID
                JOIN Booking B ON T.BookingID = B.BookingID
                WHERE B.FlightID = %s
            """, (flight_id,))
            results['requests_flight'] = cursor.fetchall()

    except Exception as e:
        print("Error fetching data:", e)
        flash("Error executing query", "error")

    return render_template('booking_details.html',
                           action=action,
                           **results,
                           user_id=user_id,
                           flight_id=flight_id)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))


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


@app.route('/manage-flights')
def manage_flights():
    flights = get_all_flights()
    return render_template('flight_management.html', flights=flights)


if __name__ == '__main__':
    app.run(debug=True)
