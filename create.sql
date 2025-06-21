CREATE TABLE UserAccount (
    UserID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    LoyaltyPoints INT DEFAULT 0
);

CREATE TABLE Passenger (
    PassengerID SERIAL PRIMARY KEY,
    UserID INT REFERENCES UserAccount(UserID) ON DELETE CASCADE,
    BookingID INT,
    SeatID INT,
    DateOfBirth DATE NOT NULL,
    Address TEXT,
    IDNumber VARCHAR(50) NOT NULL,
    Nationality VARCHAR(50) NOT NULL
);

CREATE TABLE Flight (
    FlightID SERIAL PRIMARY KEY,
    AirlineName VARCHAR(100) NOT NULL,
    FlightNumber VARCHAR(20) UNIQUE NOT NULL,
    Source VARCHAR(50) NOT NULL,
    Destination VARCHAR(50) NOT NULL,
    DepartureTime TIMESTAMP NOT NULL,
    ArrivalTime TIMESTAMP NOT NULL,
    Duration INTERVAL NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('On-Time', 'Delayed', 'Canceled')),
    FlightType VARCHAR(20) CHECK (FlightType IN ('Non-Stop', 'Connected'))
);

ALTER SEQUENCE flight_flightid_seq RESTART WITH 1;

CREATE TABLE FlightClass (
    ClassID SERIAL PRIMARY KEY,
    FlightID INT REFERENCES Flight(FlightID) ON DELETE CASCADE,
    ClassType VARCHAR(20) CHECK (ClassType IN ('Economy', 'Business', 'First Class')),
    TotalSeats INT CHECK (TotalSeats > 0),
    AvailableSeats INT CHECK (AvailableSeats >= 0),
    PricePerSeat DECIMAL(10,2) CHECK (PricePerSeat > 0),
    UNIQUE (FlightID, ClassType)  
);


CREATE TABLE Airport (
    AirportID SERIAL PRIMARY KEY,
    AirportName VARCHAR(100) NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Country VARCHAR(50) NOT NULL,
    IATA_Code CHAR(3) UNIQUE NOT NULL
);

CREATE TABLE Booking (
    BookingID SERIAL PRIMARY KEY,
    PassengerID INT REFERENCES Passenger(PassengerID) ON DELETE CASCADE,
    FlightID INT REFERENCES Flight(FlightID) ON DELETE CASCADE,
    BookingDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    --TravelDate DATE NOT NULL,
   -- SeatNumber VARCHAR(5) NOT NULL,
   -- ClassType VARCHAR(15) CHECK (ClassType IN ('Economy', 'Business', 'First Class')),
    Status VARCHAR(10) CHECK (Status IN ('Confirmed', 'Canceled', 'Pending'))
);

CREATE TABLE Payments (
    PaymentID SERIAL PRIMARY KEY,
    BookingID INT REFERENCES Booking(BookingID) ON DELETE CASCADE,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    AmountPaid DECIMAL(10,2) NOT NULL,
    PaymentMethod VARCHAR(50) CHECK (PaymentMethod IN ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Wallets')),
    TransactionID VARCHAR(50) UNIQUE NOT NULL,
    PaymentStatus VARCHAR(15) CHECK (PaymentStatus IN ('Success', 'Pending', 'Failed', 'Refunded'))
   );

CREATE TABLE Seat (
    SeatID SERIAL PRIMARY KEY,
    FlightID INT REFERENCES Flight(FlightID) ON DELETE CASCADE,
    SeatNumber VARCHAR(5) NOT NULL,
    ClassType VARCHAR(15) CHECK (ClassType IN ('Economy', 'Business', 'First Class')),
    Status VARCHAR(10) CHECK (Status IN ('Available', 'Booked', 'Blocked')),
    Price DECIMAL(10,2) NOT NULL
);

CREATE TABLE SpecialRequests (
    RequestID SERIAL PRIMARY KEY,
    BookingID INT REFERENCES Booking(BookingID) ON DELETE CASCADE,
    PassengerID INT REFERENCES Passenger(PassengerID) ON DELETE CASCADE,
    RequestType VARCHAR(50) CHECK (RequestType IN ('Wheelchair', 'Pet', 'Personal Assistance')),
    RequestDetails TEXT,
    Status VARCHAR(10) CHECK (Status IN ('Pending', 'Approved', 'Denied')),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ResolvedDate TIMESTAMP
);

CREATE TABLE Admin (
    AdminID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(15) UNIQUE NOT NULL
);

CREATE TABLE Ticket (
    TicketID SERIAL PRIMARY KEY,
    BookingID INT REFERENCES Booking(BookingID) ON DELETE CASCADE,
    PassengerID INT REFERENCES Passenger(PassengerID) ON DELETE CASCADE,
    SeatID INT REFERENCES Seat(SeatID) ON DELETE CASCADE,
    FlightID INT REFERENCES Flight(FlightID) ON DELETE CASCADE,
    SeatNumber VARCHAR(5) NOT NULL,
    ClassType VARCHAR(15) CHECK (ClassType IN ('Economy', 'Business', 'First Class')),
    SpecialRequestID INT REFERENCES SpecialRequests(RequestID) ON DELETE SET NULL,
    TicketStatus VARCHAR(10) CHECK (TicketStatus IN ('Booked', 'Canceled', 'Pending'))
);









