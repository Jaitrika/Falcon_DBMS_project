from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

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
