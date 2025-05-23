from datetime import datetime
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

@app.route('/select_seat/<int:flight_id>/<int:booking_id>',methods=['GET', 'POST'])
def select_seat(flight_id, booking_id):
    cursor = conn.cursor(dictionary=True)
    travel_class = session.get('travel_class')
    cursor.execute("""
            SELECT ClassType, TotalSeats
            FROM FlightClass
            WHERE FlightID = %s
            AND ClassType = %s
        """, (flight_id, travel_class))
    classes = cursor.fetchall()

    # Step 2: Get all booked seat numbers
    cursor.execute("""
        SELECT SeatNumber
        FROM Seat
        WHERE FlightID = %s
    """, (flight_id,))
    booked = set(row['SeatNumber'] for row in cursor.fetchall())

    layout_config = {
        'Economy': 6,   # 6 seats per row
        'Business': 4,
        'First': 4
    }
    seat_map = {}
    # Step 3: Generate seat grid per class
    for cls in classes:
        class_type = cls['ClassType']
        total_seats = cls['TotalSeats']
        seats_per_row = layout_config.get(class_type, 6)  # Default to 6 seats if not defined
        rows = total_seats // seats_per_row + (1 if total_seats % seats_per_row != 0 else 0)  # Calculate rows needed

        seat_grid = []
        seat_number = 1

        for r in range(rows):
            row = []
            for c in range(seats_per_row):
                if seat_number > total_seats:
                    break
                col_letter = chr(65 + c)  # A, B, C, ...
                seat_code = f"{r + 1}{col_letter}"
                row.append({
                    'seat': seat_code,
                    'booked': seat_code in booked
                })
                seat_number += 1
            seat_grid.append(row)

        seat_map[class_type] = seat_grid
    cursor.close()
    if request.method == 'POST':
        selected_seats = request.form.get('selected_seats', '').split(',')
        session['selected_seats'] = selected_seats
        print("hihihi", selected_seats)
        return redirect(url_for('payment', booking_id=booking_id))

    return render_template('seat_selection.html', seat_map=seat_map, flight_id=flight_id, booking_id=booking_id)

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
        elif action == 'approve_request':
            request_id = request.args.get('request_id')
            if request_id:
                try:
                    cursor.execute("""
                        UPDATE SpecialRequests
                        SET Status = 'Approved'
                        WHERE RequestID = %s AND Status != 'Approved'
                    """, (request_id,))
                    conn.commit()
                    flash(f"Request ID {request_id} approved successfully.", "success")
                except Exception as e:
                    print("Error approving request:", e)
                    flash("Failed to approve special request.", "error")

    except Exception as e:
        print("Error fetching data:", e)
        flash("Error executing query", "error")

    return render_template('booking_details.html',
                           action=action,
                           **results,
                           user_id=user_id,
                           flight_id=flight_id)

@app.route('/account')
def account():
    if 'userid' not in session:
        flash('Please log in to view your account.', 'error')
        return redirect(url_for('login'))

    print("User ID from session:", session['userid'])

    cursor = conn.cursor(dictionary=True)
    try:
        userid=session.get('userid')
        cursor.execute("SELECT * FROM useraccount WHERE UserID = %s", (userid,))
        user = cursor.fetchone()
        print("Fetched user:", user)
        return render_template('account.html', user=user)
    except Exception as e:
        print("Error fetching user data:", e)
        flash("Unable to load account data.", "error")
        return render_template('account.html',user=None)

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

@app.route('/searchFlight')
def searchFlight():
    booking_info = session.get('booking_info', {})
    print(booking_info)
    src = booking_info.get('source')
    dest = booking_info.get('destination')
    departure_date_str = booking_info.get('departure_date_str')
    # if not departure_date_str:
        # print("Missing departure date in session")
        # return redirect(url_for('booking'))

    departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
    departure_date=str(departure_date)
    TravelClass = booking_info.get('travel_class')
    required_seats = booking_info.get('required_seats')

    cursor = conn.cursor(dictionary=True)  # make sure to define cursor here
    query = """
        SELECT f.*, fc.ClassType, fc.PricePerSeat, fc.AvailableSeats
        FROM flight f
        JOIN flightclass fc ON f.FlightID = fc.FlightID
        WHERE f.Source = %s AND f.Destination = %s AND DATE(f.DepartureTime) = %s AND fc.ClassType= %s
    """
    cursor.execute(query, (src, dest, departure_date, TravelClass))
    results = cursor.fetchall()

    price_sort = request.args.get('price_sort', 'none')

    if price_sort == 'asc':
        results.sort(key=lambda x: x['PricePerSeat'])
    elif price_sort == 'desc':
        results.sort(key=lambda x: x['PricePerSeat'], reverse=True)

    filtered_results = [
        flight for flight in results
        if flight['AvailableSeats'] >= required_seats
    ]

    if not filtered_results:
        flash("No matching flights found", "info")

    return render_template('searchFlight.html', flights=filtered_results, price_sort=price_sort)


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
        departure_date_str = request.form.get('departure_date')
        print(departure_date_str)
        # departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
        TravelClass = request.form.get('TravelClass')

        session['travel_class'] = TravelClass

        adults = int(request.form.get('adults', 0))
        children = int(request.form.get('children', 0))
        required_seats = adults + children

        session['num_passengers'] = required_seats

        session['booking_info'] = {
            'source': src,
            'destination': dest,
            'departure_date_str': departure_date_str,
            'travel_class': TravelClass,
            'adults': adults,
            'children': children,
            'required_seats': required_seats
        }

        try:
            # booking_info = session.get('booking_info', {})

            # src = booking_info.get('source')
            # dest = booking_info.get('destination')
            # departure_date = booking_info.get('departure_date_str')
            # departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
            # TravelClass = booking_info.get('travel_class')
            # required_seats = booking_info.get('required_seats')

            # query = """
            #     SELECT f.*, fc.ClassType, fc.PricePerSeat, fc.AvailableSeats
            #     FROM flight f
            #     JOIN flightclass fc ON f.FlightID = fc.FlightID
            #     WHERE f.Source = %s AND f.Destination = %s AND DATE(f.DepartureTime) = %s AND fc.ClassType= %s"""
            # cursor.execute(query, (src, dest, departure_date, TravelClass))
            # results = cursor.fetchall()

            # price_sort = request.args.get('price_sort', 'none')

            # if price_sort == 'asc':
            #     results.sort(key=lambda x: x['PricePerSeat'])
            # elif price_sort == 'desc':
            #     results.sort(key=lambda x: x['PricePerSeat'], reverse=True)

            # filtered_results=[
            #     flight for flight in results
            #     if flight['AvailableSeats'] >= required_seats
            # ]

            # session['filtered_results'] = json.dumps(filtered_results)

            # if not results:
            #     flash("No matching flights found", "info")

            return redirect(url_for('searchFlight'))

            # return render_template('searchFlight.html', flights=filtered_results, price_sort=price_sort)

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
        return redirect(url_for('select_seat', flight_id=flight_id,booking_id=booking_id))

    return render_template('booking2.html', flight_id=flight_id, num_passengers=num_passengers,
                           travel_class=travel_class)


@app.route('/payment/<int:booking_id>', methods=['GET','POST'])
def payment(booking_id):
    cursor = conn.cursor()

    # Get FlightID
    cursor.execute("SELECT FlightID FROM booking WHERE BookingID = %s", (booking_id,))
    result = cursor.fetchone()
    if result is None:
        flash("Invalid booking ID.", "error")
        return redirect(url_for('home'))
    flight_id = result[0]

    # Get passengers
    cursor.execute("SELECT PassengerID FROM passenger WHERE BookingID = %s", (booking_id,))
    passenger_ids = cursor.fetchall()
    print(passenger_ids)

    travel_class = session.get('travel_class')
    if not travel_class:
        flash("Travel class info missing. Please restart booking.", "error")
        return redirect(url_for('home'))

    # Get price
    cursor.execute("""
        SELECT PricePerSeat FROM flightclass
        WHERE FlightID = %s AND ClassType = %s
    """, (flight_id, travel_class))
    price_result = cursor.fetchone()
    if not price_result:
        flash("Unable to fetch price info.", "error")
        return redirect(url_for('home'))

    price_per_seat = price_result[0]
    total_price = price_per_seat * len(passenger_ids)

    return render_template('payment.html',
                           booking_id=booking_id,
                           flight_id=flight_id,
                           total_price=total_price)

@app.route('/confirm_payment/<int:booking_id>', methods=['POST'])
def confirm_payment(booking_id):
    cursor = conn.cursor()

    # Get flight and passengers
    cursor.execute("SELECT FlightID FROM booking WHERE BookingID = %s", (booking_id,))
    result = cursor.fetchone()
    if not result:
        flash("Invalid booking ID.", "error")
        return redirect(url_for('home'))
    flight_id = result[0]

    cursor.execute("SELECT PassengerID FROM passenger WHERE BookingID = %s", (booking_id,))
    passenger_ids = cursor.fetchall()


    travel_class = session.get('travel_class')
    # selected_seats = request.form.get('selected_seats', '').split(',')
    print(passenger_ids)
    selected_seats=session['selected_seats']
    print(selected_seats)
    #print("Form passenger data:", request.form)

    if len(selected_seats) != len(passenger_ids):
        flash("Mismatch between seats and passengers.", "error")
        return redirect(url_for('home'))

    total_price = 0
    for i, (passenger_id,) in enumerate(passenger_ids):
        seat_number = selected_seats[i]

        # Check if seat is already booked
        cursor.execute("""
            SELECT * FROM seat
            WHERE FlightID = %s AND SeatNumber = %s AND ClassType = %s AND Status = 'Booked'
        """, (flight_id, seat_number, travel_class))
        if cursor.fetchone():
            flash(f"Seat {seat_number} is already booked.", "error")
            return redirect(url_for('home'))

        # Get price
        cursor.execute("""
            SELECT PricePerSeat FROM flightclass
            WHERE FlightID = %s AND ClassType = %s
        """, (flight_id, travel_class))
        price = cursor.fetchone()[0]
        total_price += price

        # Insert seat
        cursor.execute("""
            INSERT INTO seat (FlightID, SeatNumber, ClassType, Status, Price)
            VALUES (%s, %s, %s, 'Booked', %s)
        """, (flight_id, seat_number, travel_class, price))
        seat_id = cursor.lastrowid

        # Insert ticket
        cursor.execute("""
            INSERT INTO ticket (BookingID, PassengerID, SeatID)
            VALUES (%s, %s, %s)
        """, (booking_id, passenger_id, seat_id))
        ticket_id = cursor.lastrowid

        # Update passenger
        cursor.execute("""
            UPDATE passenger SET SeatID = %s WHERE PassengerID = %s
        """, (seat_id, passenger_id))

        # Update seat availability
        cursor.execute("""
            UPDATE flightclass
            SET AvailableSeats = GREATEST(AvailableSeats - 1, 0)
            WHERE FlightID = %s AND ClassType = %s
        """, (flight_id, travel_class))

        # Special requests
        special_request = session['special_requests'].get(str(passenger_id), '')
        if special_request:
            cursor.execute("""
                INSERT INTO specialrequests (RequestDetails, TicketID)
                VALUES (%s, %s)
            """, (special_request, ticket_id))
            special_request_id = cursor.lastrowid
            cursor.execute("""
                UPDATE ticket SET SpecialRequestID = %s WHERE TicketID = %s
            """, (special_request_id, ticket_id))

    cursor.execute("UPDATE booking SET Status = 'Confirmed' WHERE BookingID = %s", (booking_id,))
    conn.commit()
    cursor.close()

    flash("Payment successful! Tickets have been booked.", "success")
    return redirect(url_for('view_tickets', booking_id=booking_id))



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
