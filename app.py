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
                return redirect(url_for('booking'))
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

@app.route('/manage-flights', methods=['GET'])
def manage_flights():
    if 'admin_id' not in session:
        flash("Access denied. Please log in as admin.", "error")
        return redirect(url_for('admin_login'))

    action = request.args.get('action')
    cursor = conn.cursor(dictionary=True)

    # Default values for parameters
    month = request.args.get('month', type=int, default=2)
    year = request.args.get('year', type=int, default=2025)
    email = request.args.get('email')

    # Initialize variables to pass to template
    total_revenue = None
    flights = []
    users = []
    payments = []

    try:
        if action == 'monthly_revenue':
            cursor.execute("""
                SELECT SUM(P.AmountPaid) AS TotalRevenue
                FROM Payments P
                WHERE P.PaymentStatus = 'Success'
                  AND MONTH(P.PaymentDate) = %s
                  AND YEAR(P.PaymentDate) = %s
            """, (month, year))
            result = cursor.fetchone()
            total_revenue = result['TotalRevenue'] if result and result['TotalRevenue'] else 0

        elif action == 'low_booking_flights':
            cursor.execute("""
                SELECT F.FlightID, F.FlightNumber, F.AirlineName, F.Source, F.Destination, 
                       COUNT(B.BookingID) AS TotalBookings
                FROM Flight F
                LEFT JOIN Booking B ON F.FlightID = B.FlightID
                GROUP BY F.FlightID
                HAVING TotalBookings < 3
            """)
            flights = cursor.fetchall()

        elif action == 'frequent_users':
            cursor.execute("""
                SELECT UA.UserID, UA.Name, UA.Email, COUNT(B.BookingID) AS TotalBookings
                FROM UserAccount UA
                JOIN Booking B ON UA.UserID = B.UserID
                GROUP BY UA.UserID
                HAVING TotalBookings > 1
            """)
            users = cursor.fetchall()

        elif action == 'pending_payments' and email:
            cursor.execute("""
                SELECT p.*
                FROM Payments p
                JOIN Booking b ON p.BookingID = b.BookingID
                JOIN UserAccount u ON b.UserID = u.UserID
                WHERE u.Email = %s AND p.PaymentStatus = 'Pending'
            """, (email,))
            payments = cursor.fetchall()

    except Exception as e:
        print("Error in manage_flights:", e)
        flash("An error occurred while fetching data.", "error")

    return render_template('flight_management.html',
                           action=action,
                           total_revenue=total_revenue,
                           month=month,
                           year=year,
                           flights=flights,
                           users=users,
                           pending_payments=payments,
                           email=email)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    cursor = conn.cursor(dictionary=True)

    # Fetch dropdown options always
    cursor.execute("SELECT DISTINCT Source FROM flight")
    source = [row['Source'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT Destination FROM flight")
    destination = [row['Destination'] for row in cursor.fetchall()]

    # Handle form submission
    if request.method == 'POST':
        src = request.form.get('source')
        dest = request.form.get('destination')
        departure_date = request.form.get('departure_date')
        TravelClass = request.form.get('TravelClass')

        session['travel_class'] = TravelClass

        adults = int(request.form.get('adults', 0))
        children = int(request.form.get('children', 0))
        required_seats = adults + children

        session['num_passengers'] = required_seats

        try:
            query = """
                SELECT f.*, fc.ClassType, fc.PricePerSeat, fc.AvailableSeats
                FROM flight f
                JOIN flightclass fc ON f.FlightID = fc.FlightID
                WHERE f.Source = %s AND f.Destination = %s AND DATE(f.DepartureTime) = %s AND fc.ClassType= %s"""
            cursor.execute(query, (src, dest, departure_date, TravelClass))
            results = cursor.fetchall()
            print("search flight hihihihihi sad")

            filtered_results = [
                flight for flight in results
                if flight['AvailableSeats'] >= required_seats
            ]

            if not results:
                flash("No matching flights found", "info")

            return render_template('searchFlight.html', flights=filtered_results)

        except Exception as e:
            print("Search error:", e)
            flash("Something went wrong during the search.", "error")
            return redirect(url_for('booking'))

    return render_template('booking.html', source=source, destination=destination)


@app.route('/booking2/<int:flight_id>', methods=['GET', 'POST'])
def booking2(flight_id):
    if 'userid' not in session:
        flash('Please login to book a flight.', 'error')
        return redirect(url_for('login'))

    num_passengers = session.get('num_passengers')
    travel_class = session.get('travel_class')

    if request.method == 'POST':
        cursor = conn.cursor()

        # 1. Create the booking record
        booking_query = """
            INSERT INTO booking (FlightID, UserID, Status)
            VALUES (%s, %s, 'Pending')
        """
        cursor.execute(booking_query, (flight_id, session['userid']))
        conn.commit()

        booking_id = cursor.lastrowid  # Newly created booking ID

        passenger_query = """
            INSERT INTO passenger (UserID, BookingID, Name, DateOfBirth, Address, IDNumber, Nationalitya, TravelType)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

        """

        passenger_ids = []
        passenger_details = {}  # Dictionary to store PassengerID and special requests

        for i in range(num_passengers):
            name = request.form.get(f'name_{i}')
            dob = request.form.get(f'dob_{i}')
            address = request.form.get(f'address_{i}')
            id_number = request.form.get(f'id_number_{i}')
            nationality = request.form.get(f'nationality_{i}')
            travel_type = request.form.get(f'travel_type_{i}')
            special_request = request.form.get(f'special_requests_{i}', '')  # Default to empty string if not provided

            # Ensure that the passenger's data is valid
            if not dob or not address or not id_number or not nationality or not travel_type:
                flash(f"Missing required details for passenger {i + 1}.", "error")
                return redirect(url_for('booking2', flight_id=flight_id))

            # Insert into passenger table
            cursor.execute(passenger_query, (
                session['userid'],
                booking_id,
                name,
                dob,
                address,
                id_number,
                nationality,
                travel_type
            ))

            conn.commit()

            # Get the actual PassengerID from the last insert
            passenger_id = cursor.lastrowid

            # Store passenger special request with the actual PassengerID in the dictionary
            passenger_details[passenger_id] = special_request

        # Store the passenger special requests in the session after processing all passengers
        session['special_requests'] = passenger_details

        cursor.close()

        # Redirect to payment after successfully processing the booking
        return redirect(url_for('payment', booking_id=booking_id))

    return render_template('booking2.html', flight_id=flight_id, num_passengers=num_passengers,
                           travel_class=travel_class)


import random
@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    cursor = conn.cursor()

    # Get FlightID
    cursor.execute("SELECT FlightID FROM booking WHERE BookingID = %s", (booking_id,))
    result = cursor.fetchone()
    if result is None:
        flash("Invalid booking ID.", "error")
        return redirect(url_for('home'))
    flight_id = result[0]

    # Get passengers for this booking
    cursor.execute("SELECT PassengerID FROM passenger WHERE BookingID = %s", (booking_id,))
    passenger_ids = cursor.fetchall()

    travel_class = session.get('travel_class')
    if not travel_class:
        flash("Travel class info missing. Please restart booking.", "error")
        return redirect(url_for('home'))

    # Get price per seat
    cursor.execute("""
        SELECT PricePerSeat FROM flightclass
        WHERE FlightID = %s AND ClassType = %s
    """, (flight_id, travel_class))
    price_result = cursor.fetchone()
    if not price_result:
        flash("Unable to fetch price info.", "error")
        return redirect(url_for('home'))

    price_per_seat = price_result[0]
    num_passengers = len(passenger_ids)
    total_price = price_per_seat * num_passengers

    if request.method == 'POST':
        # POST logic stays the same as before
        for (passenger_id,) in passenger_ids:
            # Generate a unique seat
            while True:
                seat_number = f"{random.randint(1, 50)}{random.choice(['A', 'B', 'C', 'D'])}"
                cursor.execute("""
                    SELECT * FROM seat
                    WHERE FlightID = %s AND SeatNumber = %s AND ClassType = %s
                """, (flight_id, seat_number, travel_class))
                if not cursor.fetchone():
                    break  # seat is available

            # Get price for class
            cursor.execute("""
                SELECT PricePerSeat FROM flightclass
                WHERE FlightID = %s AND ClassType = %s
            """, (flight_id, travel_class))
            price_result = cursor.fetchone()
            if price_result is None:
                flash(f"Class {travel_class} not available for this flight.", "error")
                return redirect(url_for('home'))
            price = price_result[0]
            total_price += price  # Add price for this passenger

            # Insert into seat table
            cursor.execute("""
                INSERT INTO seat (FlightID, SeatNumber, ClassType, Status, Price)
                VALUES (%s, %s, %s, 'Booked', %s)
            """, (flight_id, seat_number, travel_class, price))
            seat_id = cursor.lastrowid

            # Insert into ticket table
            cursor.execute("""
                INSERT INTO ticket (BookingID, PassengerID, SeatID)
                VALUES (%s, %s, %s)
            """, (booking_id, passenger_id, seat_id))
            ticket_id = cursor.lastrowid  # Get the ticket ID for this passenger

            # Update passenger table with assigned SeatID
            cursor.execute("""
                UPDATE passenger SET SeatID = %s WHERE PassengerID = %s
            """, (seat_id, passenger_id))

            cursor.execute("""
                UPDATE flightclass
                SET AvailableSeats = GREATEST(AvailableSeats - 1, 0)
                WHERE FlightID = %s AND ClassType = %s
            """, (flight_id, travel_class))

            # Insert special request into special_requests table if any
            special_request = session['special_requests'].get(str(passenger_id), '')  # Fetch the special request
            if special_request:
                cursor.execute("""
                                INSERT INTO specialrequests (RequestDetails, TicketID)
                                VALUES (%s, %s)
                            """, (special_request, ticket_id))
                special_request_id = cursor.lastrowid  # Get SpecialRequestID

                # Update the ticket table with the SpecialRequestID
                cursor.execute("""
                                UPDATE ticket SET SpecialRequestID = %s WHERE TicketID = %s
                            """, (special_request_id, ticket_id))

        # Update booking status to Confirmed
        cursor.execute("UPDATE booking SET Status = 'Confirmed' WHERE BookingID = %s", (booking_id,))

        conn.commit()
        cursor.close()
        flash("Payment successful! Tickets have been booked.", "success")
        return redirect(url_for('view_tickets', booking_id=booking_id))

    # If GET request, just render page with actual total
    return render_template('payment.html',
                           flight_id=flight_id,
                           booking_id=booking_id,
                           total_price=total_price)

@app.route('/tickets/<int:booking_id>')
def view_tickets(booking_id):
    cursor = conn.cursor()

    # Get booking and flight details
    cursor.execute("""
        SELECT b.BookingID, f.AirlineName, f.FlightNumber, f.Source, f.Destination, f.DepartureTime, f.ArrivalTime
        FROM booking b
        JOIN flight f ON b.FlightID = f.FlightID
        WHERE b.BookingID = %s
    """, (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for('home'))

    # Get ticket, passenger details from useraccount, seat info, and special request info
    cursor.execute("""
        SELECT t.TicketID, p.Name AS PassengerName, p.Nationalitya, 
               s.SeatNumber, s.ClassType, s.Price, 
               sr.RequestDetails AS SpecialRequest
        FROM ticket t
        JOIN passenger p ON t.PassengerID = p.PassengerID
        JOIN seat s ON t.SeatID = s.SeatID
        LEFT JOIN specialrequests sr ON t.SpecialRequestID = sr.RequestID
        WHERE t.BookingID = %s
    """, (booking_id,))

    tickets = cursor.fetchall()

    return render_template('ticket_summary.html', booking=booking, tickets=tickets)


if __name__ == '__main__':
    app.run(debug=True)
