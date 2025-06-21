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
                        src.Location AS Source, dest.Location AS Destination, 
                        F.DepartureTime, B.Status AS BookingStatus
                 FROM Booking B
                 JOIN Flight F ON B.FlightID = F.FlightID
                 JOIN airport src ON F.SourceIATA = src.IATA_Code
                 JOIN airport dest ON F.DestinationIATA = dest.IATA_Code
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
                src.Location AS Source, dest.Location AS Destination,
                F.DepartureTime, B.Status AS BookingStatus,
                P.PaymentID, P.AmountPaid, P.PaymentStatus
         FROM Booking B
         LEFT JOIN Payments P ON B.BookingID = P.BookingID
         JOIN Flight F ON B.FlightID = F.FlightID
         JOIN airport src ON F.SourceIATA = src.IATA_Code
         JOIN airport dest ON F.DestinationIATA = dest.IATA_Code
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

                    admin_id = session['admin_id']

                    cursor.execute("""
                                        INSERT INTO AdminActions (AdminID, ActionType, RequestID) VALUES (%s, %s, %s)""",
                                   (admin_id, 'Approve Request', request_id))
                    conn.commit()
                    flash("Request approved.", "success")
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

@app.route('/manage-flights', methods=['GET', 'POST'])
def manage_flights():
    if 'admin_id' not in session:
        flash("Access denied. Please log in as admin.", "error")
        return redirect(url_for('admin_login'))

    action = request.form.get('action') if request.method == 'POST' else request.args.get('action')

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
        print("hi")
        if request.method == 'POST' and action == 'add_flight':
            print("hihi")
            flight_number = request.form['flight_number']
            airline_name = request.form['airline_name']
            source = request.form['source']
            destination = request.form['destination']
            departure_time = request.form['departure_time']
            arrival_time = request.form['arrival_time']
            duration = request.form['duration']
            status = request.form['status']
            flight_type = request.form['flight_type']

            cursor.execute("""
                INSERT INTO Flight (AirlineName,FlightNumber, SourceIATA, DestinationIATA, DepartureTime, ArrivalTime,Duration,Status,FlightType)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (airline_name, flight_number, source, destination, departure_time, arrival_time, duration, status,
                  flight_type))
            conn.commit()

            flight_id = cursor.lastrowid

            economy_seats = int(request.form['economy_seats'])
            economy_price = float(request.form['economy_price'])

            business_seats = int(request.form['business_seats'])
            business_price = float(request.form['business_price'])

            first_class_seats = int(request.form.get('first_class_seats'))
            first_class_price = float(request.form.get('first_class_price'))

            cursor.execute("""
                INSERT INTO FlightClass (FlightID, ClassType, TotalSeats, AvailableSeats, PricePerSeat)
                VALUES (%s, %s, %s, %s, %s)
            """, (flight_id, 'Economy', economy_seats, economy_seats, economy_price))

            if business_seats > 0:
                cursor.execute("""
                    INSERT INTO FlightClass (FlightID, ClassType, TotalSeats, AvailableSeats, PricePerSeat)
                    VALUES (%s, %s, %s, %s, %s)
                """, (flight_id, 'Business', business_seats, business_seats, business_price))

            if first_class_seats > 0:
                cursor.execute("""
                    INSERT INTO FlightClass (FlightID, ClassType, TotalSeats, AvailableSeats, PricePerSeat)
                    VALUES (%s, %s, %s, %s, %s)
                """, (flight_id, 'First Class', first_class_seats, first_class_seats, first_class_price))

            conn.commit()

            # Log admin action
            admin_id = session['admin_id']
            cursor.execute("""
            INSERT INTO AdminActions (AdminID, ActionType, FlightID)
            VALUES (%s, %s, %s)""", (admin_id, 'Add Flight', flight_id))
            conn.commit()
            print("hihihi")
            flash("Flight added successfully!", "success")

        elif request.method == 'POST' and action == 'delete_flight':
            flight_id = request.form.get('flight_id')
            cursor.execute("UPDATE Flight SET Status = %s WHERE FlightID = %s", ('Canceled', flight_id))
            conn.commit()
            admin_id = session['admin_id']
            cursor.execute("""
            INSERT INTO AdminActions (AdminID, ActionType, FlightID)
            VALUES (%s, %s, %s)
            """, (admin_id, 'Delete Flight', flight_id))
            conn.commit()
            print("hihihidel")
            flash("Flight deleted successfully!", "success")


        elif action == 'monthly_revenue':
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
                 SELECT F.FlightID, F.FlightNumber, F.AirlineName, 
               src.Location AS Source, dest.Location AS Destination,
               COUNT(B.BookingID) AS TotalBookings
        FROM Flight F
        LEFT JOIN Booking B ON F.FlightID = B.FlightID
        JOIN airport src ON F.SourceIATA = src.IATA_Code
        JOIN airport dest ON F.DestinationIATA = dest.IATA_Code
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

    departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
    departure_date=str(departure_date)
    TravelClass = booking_info.get('travel_class')
    required_seats = booking_info.get('required_seats')

    cursor = conn.cursor(dictionary=True)  # make sure to define cursor here

    query = """
        SELECT f.*, 
               src.Location AS Source, 
               dest.Location AS Destination,
               fc.ClassType, fc.PricePerSeat, fc.AvailableSeats
        FROM flight f
        JOIN flightclass fc ON f.FlightID = fc.FlightID
        JOIN airport src ON f.SourceIATA = src.IATA_Code
        JOIN airport dest ON f.DestinationIATA = dest.IATA_Code
        WHERE f.SourceIATA = %s AND f.DestinationIATA = %s 
              AND DATE(f.DepartureTime) = %s AND fc.ClassType = %s
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

    # Fetch unique airport locations for dropdown (not IATA)
    cursor.execute("SELECT DISTINCT Location FROM Airport")
    source = [row['Location'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT Location FROM Airport")
    destination = [row['Location'] for row in cursor.fetchall()]

    if request.method == 'POST':
        src_location = request.form.get('source')
        dest_location = request.form.get('destination')
        departure_date_str = request.form.get('departure_date')
        TravelClass = request.form.get('TravelClass')

        adults = int(request.form.get('adults', 0))
        children = int(request.form.get('children', 0))
        required_seats = adults + children

        # Convert Location to IATA Code using Airport table
        cursor.execute("SELECT IATA_Code FROM Airport WHERE Location = %s", (src_location,))
        src_row = cursor.fetchone()
        src = src_row['IATA_Code'] if src_row else None

        cursor.execute("SELECT IATA_Code FROM Airport WHERE Location = %s", (dest_location,))
        dest_row = cursor.fetchone()
        dest = dest_row['IATA_Code'] if dest_row else None

        if not src or not dest:
            flash("Invalid source or destination selected.", "error")
            return redirect(url_for('booking'))

        # Store both IATA codes and locations in session
        session['travel_class'] = TravelClass
        session['num_passengers'] = required_seats
        session['booking_info'] = {
            'source': src,                         # IATA Code for query
            'destination': dest,                   # IATA Code for query
            'source_location': src_location,       # For display
            'destination_location': dest_location, # For display
            'departure_date_str': departure_date_str,
            'travel_class': TravelClass,
            'adults': adults,
            'children': children,
            'required_seats': required_seats
        }
        try:
            return redirect(url_for('searchFlight'))
        except Exception as e:
            print("Search error:", e)
            flash("Something went wrong during the search.", "error")
            return redirect(url_for('booking'))

    return render_template('booking.html', source=source, destination=destination)
from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import datetime

@app.route('/booking2/<int:flight_id>', methods=['GET', 'POST'])
def booking2(flight_id):
    print("Method:", request.method, "| booking_id in session:", session.get('booking_id'))

    if 'userid' not in session:
        flash('Please login to book a flight.', 'error')
        return redirect(url_for('login'))

    num_passengers = session.get('num_passengers')
    travel_class = session.get('travel_class')

    if request.method == 'POST':
        cursor = conn.cursor()

        # Print form for debug
        print("Form data received:", request.form)

        passenger_details = {}

        # Validate all passenger details first
        for i in range(num_passengers):
            name = request.form.get(f'name_{i}')
            dob = request.form.get(f'dob_{i}')
            address = request.form.get(f'address_{i}')
            id_number = request.form.get(f'id_number_{i}')
            nationality = request.form.get(f'nationality_{i}')
            travel_type = request.form.get(f'travel_type_{i}')
            special_request = request.form.get(f'special_requests_{i}', '')

            if not all([name, dob, address, id_number, nationality, travel_type]):
                flash(f"Missing required details for passenger {i + 1}. Please fill out all fields.", 'error')
                print(f"[ERROR] Passenger {i+1} missing fields -> name={name}, dob={dob}, address={address}, id={id_number}, nationality={nationality}, travel_type={travel_type}")
                return redirect(request.url)

            passenger_details[i] = {
                "name": name,
                "dob": dob,
                "address": address,
                "id_number": id_number,
                "nationality": nationality,
                "travel_type": travel_type,
                "special_request": special_request
            }

        # If valid and booking not yet created, insert into booking + payments
        if 'booking_id' not in session:
            # 1. Insert booking
            booking_query = """
                INSERT INTO booking (FlightID, UserID, Status)
                VALUES (%s, %s, 'Pending')
            """
            cursor.execute(booking_query, (flight_id, session['userid']))
            conn.commit()

            booking_id = cursor.lastrowid
            session['booking_id'] = booking_id
            print("[+] Booking inserted:", booking_id)

            # 2. Insert pending payment
            payment_query = """
                INSERT INTO payments (BookingID, PaymentDate, AmountPaid, PaymentStatus)
                VALUES (%s, %s, %s, %s)
            """
            payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(payment_query, (booking_id, payment_date, 0, 'Pending'))
            conn.commit()
        else:
            booking_id = session['booking_id']
            print("[~] Using existing booking ID:", booking_id)

        # 3. Insert passenger records
        passenger_query = """
            INSERT INTO passenger (UserID, BookingID, Name, DateOfBirth, Address, IDNumber, Nationalitya, TravelType)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        special_requests_map = {}

        for i in range(num_passengers):
            data = passenger_details[i]
            cursor.execute(passenger_query, (
                session['userid'],
                booking_id,
                data['name'],
                data['dob'],
                data['address'],
                data['id_number'],
                data['nationality'],
                data['travel_type']
            ))
            conn.commit()
            passenger_id = cursor.lastrowid
            special_requests_map[passenger_id] = data['special_request']

        session['special_requests'] = special_requests_map
        cursor.close()

        return redirect(url_for('select_seat', flight_id=flight_id, booking_id=booking_id))

    return render_template('booking2.html', flight_id=flight_id, num_passengers=num_passengers, travel_class=travel_class)


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
    print(passenger_ids)
    selected_seats=session['selected_seats']
    print(selected_seats)

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

    # 3. Confirm booking
    cursor.execute("UPDATE booking SET Status = 'Confirmed' WHERE BookingID = %s", (booking_id,))
    conn.commit()

    # 4. Update the existing pending payment record
    updated_payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    payment_update_query = """
        UPDATE payments
        SET PaymentStatus = 'Success',
            PaymentDate = %s,
            AmountPaid = %s
        WHERE BookingID = %s AND PaymentStatus = 'Pending'
    """
    cursor.execute(payment_update_query, (updated_payment_date, total_price, booking_id))
    conn.commit()

    cursor.close()

    flash("Payment successful! Tickets have been booked.", "success")
    return redirect(url_for('view_tickets', booking_id=booking_id))

@app.route('/tickets/<int:booking_id>')
def view_tickets(booking_id):
    cursor = conn.cursor()

    # Get booking and flight details
    cursor.execute("""
        SELECT b.BookingID, f.AirlineName, f.FlightNumber, 
               src_airport.Location AS Source, dest_airport.Location AS Destination,
               f.DepartureTime, f.ArrivalTime
        FROM booking b
        JOIN flight f ON b.FlightID = f.FlightID
        JOIN airport src_airport ON f.SourceIATA = src_airport.IATA_Code
        JOIN airport dest_airport ON f.DestinationIATA = dest_airport.IATA_Code
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
