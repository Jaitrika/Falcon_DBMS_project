INSERT INTO UserAccount (Name, Email, PhoneNumber, Password, LoyaltyPoints) VALUES
('Aarav Sharma', 'aarav.sharma@example.com', '9876543210', 'hashed_password_1', 150),
('Ananya Iyer', 'ananya.iyer@example.com', '8765432109', 'hashed_password_2', 200),
('Rajesh Verma', 'rajesh.verma@example.com', '7654321098', 'hashed_password_3', 120),
('Pooja Nair', 'pooja.nair@example.com', '6543210987', 'hashed_password_4', 100),
('Vikram Rao', 'vikram.rao@example.com', '5432109876', 'hashed_password_5', 180),
('Neha Gupta', 'neha.gupta@example.com', '4321098765', 'hashed_password_6', 130),
('Siddharth Joshi', 'siddharth.joshi@example.com', '3210987654', 'hashed_password_7', 90),
('Meera Menon', 'meera.menon@example.com', '2109876543', 'hashed_password_8', 170),
('Karan Malhotra', 'karan.malhotra@example.com', '1098765432', 'hashed_password_9', 140),
('Divya Kulkarni', 'divya.kulkarni@example.com', '9988776655', 'hashed_password_10', 110),
('Rohan Chatterjee', 'rohan.chatterjee@example.com', '8877665544', 'hashed_password_11', 160),
('Sanya Bhatia', 'sanya.bhatia@example.com', '7766554433', 'hashed_password_12', 90),
('Arjun Deshmukh', 'arjun.deshmukh@example.com', '6655443322', 'hashed_password_13', 130),
('Priya Reddy', 'priya.reddy@example.com', '5544332211', 'hashed_password_14', 100),
('Nitin Aggarwal', 'nitin.aggarwal@example.com', '4433221100', 'hashed_password_15', 150),
('Tanvi Mishra', 'tanvi.mishra@example.com', '3322110099', 'hashed_password_16', 200),
('Yash Patel', 'yash.patel@example.com', '2211009988', 'hashed_password_17', 110),
('Sneha Saxena', 'sneha.saxena@example.com', '1100998877', 'hashed_password_18', 120),
('Amit Trivedi', 'amit.trivedi@example.com', '9988667755', 'hashed_password_19', 190),
('Lavanya Das', 'lavanya.das@example.com', '8877556644', 'hashed_password_20', 170);


ALTER TABLE Passenger ADD COLUMN TravelType TEXT;

ALTER TABLE Passenger 
ADD CONSTRAINT valid_id_check 
CHECK (
    (Nationality = 'Indian' AND TravelType = 'Domestic' AND IDNumber ~ '^[0-9]{12}$') OR
    (Nationality <> 'Indian' AND TravelType = 'Domestic' AND IDNumber ~ '^[A-Z0-9]{8,9}$') OR
    (Nationality = 'Indian' AND TravelType = 'International' AND IDNumber ~ '^[A-Z0-9]{8,9}$') OR
    (Nationality <> 'Indian' AND TravelType = 'International' AND IDNumber ~ '^[A-Z0-9]{8,9}$')
);

INSERT INTO Passenger (UserID, BookingID, SeatID, DateOfBirth, Address, IDNumber, Nationality, TravelType)
VALUES
-- Indian Domestic (Aadhaar)
(1, 101, 21, '1995-06-15', 'Mumbai, India', '123456789012', 'Indian', 'Domestic'),
(2, 102, 34, '1992-09-25', 'Delhi, India', '234567890123', 'Indian', 'Domestic'),
(3, 103, 45, '1998-04-18', 'Bangalore, India', '345678901234', 'Indian', 'Domestic'),
(4, 104, 56, '2000-12-10', 'Hyderabad, India', '456789012345', 'Indian', 'Domestic'),
(5, 105, 67, '1991-07-30', 'Kolkata, India', '567890123456', 'Indian', 'Domestic'),

-- Indian International (Passport)
(6, 106, 11, '1989-11-05', 'Pune, India', 'A12345678', 'Indian', 'International'),
(7, 107, 22, '1996-02-20', 'Chennai, India', 'B23456789', 'Indian', 'International'),
(8, 108, 33, '1994-08-12', 'Jaipur, India', 'C34567890', 'Indian', 'International'),

-- Foreign Domestic (Passport)
(9, 109, 44, '1985-05-03', 'New York, USA', 'X12345678', 'American', 'Domestic'),
(10, 110, 55, '1993-10-27', 'London, UK', 'Y23456789', 'British', 'Domestic'),
(11, 111, 66, '1997-01-15', 'Toronto, Canada', 'Z34567890', 'Canadian', 'Domestic'),

-- Foreign International (Passport)
(12, 112, 77, '1980-03-22', 'Berlin, Germany', 'D45678901', 'German', 'International'),
(13, 113, 88, '1999-09-09', 'Tokyo, Japan', 'E56789012', 'Japanese', 'International'),
(14, 114, 99, '1987-07-14', 'Sydney, Australia', 'F67890123', 'Australian', 'International'),

-- Including requested people  
(15, 115, 12, '1992-05-05', 'Pune, India', 'G78901234', 'Indian', 'International'), -- Sanya Bhatia  
(16, 116, 23, '1994-06-21', 'Delhi, India', 'H89012345', 'Indian', 'International'), -- Arjun Deshmukh  
(17, 117, 34, '1996-11-29', 'Bangalore, India', 'I90123456', 'Indian', 'International'), -- Priya Reddy  
(18, 118, 45, '1988-12-03', 'Mumbai, India', 'J01234567', 'Indian', 'International'), -- Nitin Aggarwal  
--(19, 119, 56, '1995-04-14', 'Kolkata, India', 'K12345678', 'Indian', 'Domestic'), -- Tanvi Mishra  
(20, 120, 67, '1993-08-07', 'Ahmedabad, India', 'L23456789', 'Indian', 'International'); -- Yash Patel  


TRUNCATE TABLE Flight  CASCADE;
ALTER SEQUENCE flight_flightid_seq RESTART WITH 1;



INSERT INTO Flight (AirlineName, FlightNumber, Source, Destination, DepartureTime, ArrivalTime, Duration, Status, FlightType)
VALUES 
('IndiGo', '6E101', 'Delhi', 'Mumbai', '2025-02-20 06:30:00', '2025-02-20 08:45:00', '2 hours 15 minutes', 'On-Time', 'Non-Stop'),
('Air India', 'AI202', 'Mumbai', 'London', '2025-02-20 22:00:00', '2025-02-21 06:30:00', '9 hours 30 minutes', 'On-Time', 'Non-Stop'),
('SpiceJet', 'SG303', 'Bangalore', 'Chennai', '2025-02-21 09:15:00', '2025-02-21 10:00:00', '45 minutes', 'Delayed', 'Non-Stop'),
('Lufthansa', 'LH404', 'Delhi', 'Frankfurt', '2025-02-22 13:00:00', '2025-02-22 18:00:00', '7 hours', 'On-Time', 'Non-Stop'),
('Vistara', 'UK505', 'Kolkata', 'Singapore', '2025-02-23 02:00:00', '2025-02-23 08:00:00', '6 hours', 'On-Time', 'Connected'),
('Emirates', 'EK606', 'Mumbai', 'Dubai', '2025-02-24 05:00:00', '2025-02-24 07:30:00', '2 hours 30 minutes', 'On-Time', 'Non-Stop'),
('Qatar Airways', 'QR707', 'Hyderabad', 'Doha', '2025-02-25 22:45:00', '2025-02-26 01:15:00', '3 hours 30 minutes', 'Delayed', 'Non-Stop'),
('IndiGo', '6E808', 'Delhi', 'Goa', '2025-02-26 14:00:00', '2025-02-26 16:30:00', '2 hours 30 minutes', 'On-Time', 'Non-Stop'),
('British Airways', 'BA909', 'Mumbai', 'New York', '2025-02-27 23:00:00', '2025-02-28 11:30:00', '13 hours 30 minutes', 'On-Time', 'Non-Stop'),
('Etihad Airways', 'EY1010', 'Chennai', 'Abu Dhabi', '2025-02-28 04:00:00', '2025-02-28 06:30:00', '2 hours 30 minutes', 'On-Time', 'Non-Stop'),
('GoAir', 'G8111', 'Pune', 'Delhi', '2025-03-01 18:00:00', '2025-03-01 20:15:00', '2 hours 15 minutes', 'On-Time', 'Non-Stop'),
('Singapore Airlines', 'SQ1212', 'Bangalore', 'Tokyo', '2025-03-02 01:00:00', '2025-03-02 11:30:00', '10 hours 30 minutes', 'On-Time', 'Non-Stop'),
('AirAsia', 'AK1313', 'Jaipur', 'Bangkok', '2025-03-03 08:30:00', '2025-03-03 13:30:00', '5 hours', 'On-Time', 'Connected'),
('United Airlines', 'UA1414', 'Mumbai', 'Los Angeles', '2025-03-04 00:30:00', '2025-03-04 15:00:00', '14 hours 30 minutes', 'Delayed', 'Non-Stop'),
('Cathay Pacific', 'CX1515', 'Delhi', 'Hong Kong', '2025-03-05 10:45:00', '2025-03-05 17:00:00', '6 hours 15 minutes', 'On-Time', 'Non-Stop');



INSERT INTO FlightClass (FlightID, ClassType, TotalSeats, AvailableSeats, PricePerSeat)
VALUES 
-- Flight 1: IndiGo Delhi to Mumbai
(1, 'Economy', 150, 120, 5000.00),
(1, 'Business', 30, 10, 12000.00),
(1, 'First Class', 10, 5, 20000.00),

-- Flight 2: Air India Mumbai to London
(2, 'Economy', 200, 180, 45000.00),
(2, 'Business', 50, 30, 90000.00),
(2, 'First Class', 20, 10, 150000.00),

-- Flight 3: SpiceJet Bangalore to Chennai
(3, 'Economy', 180, 160, 3000.00),
(3, 'Business', 40, 35, 7000.00),

-- Flight 4: Lufthansa Delhi to Frankfurt
(4, 'Economy', 250, 200, 60000.00),
(4, 'Business', 50, 40, 120000.00),
(4, 'First Class', 15, 10, 250000.00),

-- Flight 5: Vistara Kolkata to Singapore
(5, 'Economy', 180, 150, 25000.00),
(5, 'Business', 40, 30, 60000.00),
(5, 'First Class', 15, 5, 120000.00),

-- Flight 6: Emirates Mumbai to Dubai
(6, 'Economy', 200, 180, 20000.00),
(6, 'Business', 50, 40, 50000.00),
(6, 'First Class', 10, 8, 100000.00),

-- Flight 7: Qatar Airways Hyderabad to Doha
(7, 'Economy', 220, 200, 22000.00),
(7, 'Business', 40, 30, 60000.00),

-- Flight 8: IndiGo Delhi to Goa
(8, 'Economy', 180, 160, 4000.00),
(8, 'Business', 30, 20, 10000.00),

-- Flight 9: British Airways Mumbai to New York
(9, 'Economy', 250, 230, 70000.00),
(9, 'Business', 60, 50, 150000.00),
(9, 'First Class', 20, 10, 300000.00),

-- Flight 10: Etihad Chennai to Abu Dhabi
(10, 'Economy', 180, 170, 15000.00),
(10, 'Business', 40, 35, 40000.00),

-- Flight 11: GoAir Pune to Delhi
(11, 'Economy', 200, 180, 5000.00),
(11, 'Business', 40, 30, 12000.00),

-- Flight 12: Singapore Airlines Bangalore to Tokyo
(12, 'Economy', 240, 220, 75000.00),
(12, 'Business', 50, 45, 150000.00),
(12, 'First Class', 20, 15, 350000.00),

-- Flight 13: AirAsia Jaipur to Bangkok
(13, 'Economy', 200, 190, 18000.00),
(13, 'Business', 40, 30, 50000.00),

-- Flight 14: United Airlines Mumbai to Los Angeles
(14, 'Economy', 280, 250, 90000.00),
(14, 'Business', 60, 50, 180000.00),
(14, 'First Class', 25, 15, 400000.00),

-- Flight 15: Cathay Pacific Delhi to Hong Kong
(15, 'Economy', 230, 200, 50000.00),
(15, 'Business', 50, 40, 120000.00),
(15, 'First Class', 15, 10, 250000.00);



INSERT INTO Airport (AirportName, Location, Country, IATA_Code)
VALUES 
    ('Indira Gandhi International Airport', 'Delhi', 'India', 'DEL'),
    ('Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India', 'BOM'),
    ('Kempegowda International Airport', 'Bangalore', 'India', 'BLR'),
    ('Chennai International Airport', 'Chennai', 'India', 'MAA'),
    ('Netaji Subhas Chandra Bose International Airport', 'Kolkata', 'India', 'CCU'),
    ('Singapore Changi Airport', 'Singapore', 'Singapore', 'SIN'),
    ('Dubai International Airport', 'Dubai', 'United Arab Emirates', 'DXB'),
    ('Rajiv Gandhi International Airport', 'Hyderabad', 'India', 'HYD'),
    ('Hamad International Airport', 'Doha', 'Qatar', 'DOH'),
    ('Goa International Airport', 'Goa', 'India', 'GOI'),
    ('John F. Kennedy International Airport', 'New York', 'United States', 'JFK'),
    ('Abu Dhabi International Airport', 'Abu Dhabi', 'United Arab Emirates', 'AUH'),
    ('Pune International Airport', 'Pune', 'India', 'PNQ'),
    ('Narita International Airport', 'Tokyo', 'Japan', 'NRT'),
    ('Jaipur International Airport', 'Jaipur', 'India', 'JAI'),
    ('Suvarnabhumi Airport', 'Bangkok', 'Thailand', 'BKK'),
    ('Los Angeles International Airport', 'Los Angeles', 'United States', 'LAX'),
    ('Frankfurt Airport', 'Frankfurt', 'Germany', 'FRA'),
    ('Heathrow Airport', 'London', 'United Kingdom', 'LHR'),
    ('Hong Kong International Airport', 'Hong Kong', 'Hong Kong', 'HKG');




ALTER TABLE Booking 
ADD COLUMN UserID INT NOT NULL,
ADD CONSTRAINT FK_Booking_Passenger FOREIGN KEY (UserID) REFERENCES useraccount(UserID);
TRUNCATE TABLE booking  CASCADE;
ALTER SEQUENCE booking_bookingid_seq RESTART WITH 1;

INSERT INTO Booking (FlightID, UserID, BookingDate, Status)
VALUES
    (1, 1, '2025-02-10', 'Confirmed'),
    (2, 2, '2025-02-11', 'Pending'),
    (3, 3, '2025-02-12', 'Confirmed'),
    (4, 4, '2025-02-13', 'Canceled'),
    (5, 5, '2025-02-14', 'Confirmed'),
    (6, 6, '2025-02-15', 'Pending'),
    (7, 7, '2025-02-16', 'Confirmed'),
    (8, 8, '2025-02-17', 'Canceled'),
    (9, 9, '2025-02-18', 'Confirmed'),
    (10, 10, '2025-02-19', 'Pending'),
    (11, 11, '2025-02-20', 'Confirmed'),
    (12, 12, '2025-02-21', 'Confirmed'),
    (13, 13, '2025-02-22', 'Pending'),
    (14, 14, '2025-02-23', 'Confirmed'),
    (15, 15, '2025-02-24', 'Canceled'),
    (11, 16, '2025-02-25', 'Confirmed'),
    (12, 17, '2025-02-26', 'Pending'),
    (13, 18, '2025-02-27', 'Confirmed'),
    (14, 19, '2025-02-28', 'Canceled'),
    (15, 20, '2025-02-28', 'Confirmed');

ALTER TABLE Ticket
DROP COLUMN FlightID,
DROP COLUMN SeatNumber,
DROP COLUMN ClassType,
DROP COLUMN TicketStatus;



INSERT INTO ticket (ticketid, bookingid, passengerid, seatid, specialrequestid) VALUES
(40, 1, 1, NULL, NULL),
(42, 3, 2, NULL, NULL),
(44, 5, 3, NULL, NULL),
(46, 7, 4, NULL, NULL),
(48, 9, 5, NULL, NULL),
(41, 2, 6,NULL, NULL),
(43, 4, 7, NULL, NULL),
(45, 6, 8, NULL, NULL),
(47, 8, 9, NULL, NULL),
(49, 10, 10, NULL, NULL),
(50, 11, 11, NULL, NULL),
(55, 11, 12, NULL, NULL),
(51, 12, 13, NULL, NULL),
(56, 12, 14, NULL, NULL),
(52, 13, 15, NULL, NULL),
(57, 13, 16, NULL, NULL),
(53, 14, 17, NULL, NULL),
(58, 14, 18, NULL, NULL),
(54, 15, 19, NULL, NULL);

INSERT INTO Payments (BookingID, PaymentDate, AmountPaid, PaymentMethod, TransactionID, PaymentStatus)
VALUES
    (1, '2025-02-10 10:15:00', 7500.00, 'Credit Card', 'TXN10001', 'Success'),
    (2, '2025-02-11 12:30:00', 4200.00, 'UPI', 'TXN10002', 'Success'),
    (3, '2025-02-12 14:45:00', 8900.00, 'Debit Card', 'TXN10003', 'Pending'),
    (4, '2025-02-13 09:10:00', 5600.00, 'Net Banking', 'TXN10004', 'Success'),
    (5, '2025-02-14 16:20:00', 6200.00, 'Wallets', 'TXN10005', 'Failed'),
    (6, '2025-02-15 11:00:00', 7300.00, 'Credit Card', 'TXN10006', 'Success'),
    (7, '2025-02-16 08:50:00', 9900.00, 'Debit Card', 'TXN10007', 'Pending'),
    (8, '2025-02-17 17:30:00', 4150.00, 'UPI', 'TXN10008', 'Success'),
    (9, '2025-02-18 21:05:00', 8200.00, 'Credit Card', 'TXN10009', 'Failed'),
    (10, '2025-02-19 07:40:00', 5000.00, 'Net Banking', 'TXN10010', 'Success'),
    (11, '2025-02-20 15:55:00', 7600.00, 'Wallets', 'TXN10011', 'Pending'),
    (12, '2025-02-21 10:30:00', 9800.00, 'Debit Card', 'TXN10012', 'Success'),
    (13, '2025-02-22 18:25:00', 4500.00, 'UPI', 'TXN10013', 'Success'),
    (14, '2025-02-23 20:10:00', 8100.00, 'Credit Card', 'TXN10014', 'Failed'),
    (15, '2025-02-24 06:15:00', 6800.00, 'Net Banking', 'TXN10015', 'Success');



DROP TABLE IF EXISTS SpecialRequests CASCADE;
CREATE TABLE SpecialRequests (
    RequestID SERIAL PRIMARY KEY,
    TicketID INTEGER NOT NULL,
    RequestDetails TEXT NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('Pending', 'Approved', 'Denied')),
    FOREIGN KEY (TicketID) REFERENCES Ticket(ticketid) ON DELETE CASCADE
);

INSERT INTO SpecialRequests (RequestID, ticketID, RequestDetails, Status)
VALUES
(1, 40, 'Require Wheelchair assistance from check-in to boarding', 'Pending'),
(2, 42, 'Small dog in a carrier', 'Approved'),
(3, 44, 'Personal Assistance for Disabled', 'Pending'),
(4, 46, 'Wheelchair Assistance needed from arrival gate to exit', 'Denied'),
(5, 48, 'Cat in a soft carrier, 5kg', 'Approved');



INSERT INTO seat (seatid, flightid, seatnumber, classtype, status, price) VALUES
(1, 1, '1', 'Business', 'Booked', 12000.00),
(4, 2, '1', 'Business', 'Booked', 90000.00),
(7, 3, '1', 'Business', 'Booked', 7000.00),
(9, 4, '1', 'Business', 'Booked', 120000.00),
(12, 5, '1', 'Business', 'Booked', 60000.00),
(15, 6, '1', 'Business', 'Booked', 50000.00),
(18, 7, '1', 'Business', 'Booked', 60000.00),
(20, 8, '1', 'Business', 'Booked', 10000.00),
(22, 9, '1', 'Business', 'Booked', 150000.00),
(25, 10, '1', 'Business', 'Booked', 40000.00),
(27, 11, '1', 'Business', 'Booked', 12000.00),
(28, 11, '2', 'Business', 'Booked', 12000.00),
(31, 12, '1', 'Business', 'Booked', 150000.00),
(32, 12, '2', 'Business', 'Booked', 150000.00),
(37, 13, '1', 'Business', 'Booked', 50000.00),
(38, 13, '2', 'Business', 'Booked', 50000.00),
(41, 14, '1', 'Business', 'Booked', 180000.00),
(42, 14, '2', 'Business', 'Booked', 180000.00),
(47, 15, '1', 'Business', 'Booked', 120000.00);


UPDATE ticket t
SET seatid = (
    SELECT s.seatid
    FROM booking b
    JOIN seat s ON b.flightid = s.flightid
    WHERE b.bookingid = t.bookingid
    LIMIT 1  
)
WHERE seatid IS NULL;  



UPDATE ticket
SET specialrequestid = (
    SELECT requestid 
    FROM SpecialRequests 
    WHERE SpecialRequests.ticketID = ticket.ticketID
)
WHERE EXISTS (
    SELECT 1 FROM SpecialRequests 
    WHERE SpecialRequests.ticketID = ticket.ticketID
);

ALTER TABLE booking DROP COLUMN passengerid;

ALTER TABLE booking DROP COLUMN bookingdate;

INSERT INTO Admin (AdminID, Name, Email, PhoneNumber)
VALUES
(1, 'Amit Sharma', 'amit.sharma@airportsystem.com', '9876543210'),
(2, 'Priya Verma', 'priya.verma@airportsystem.com', '9871234567'),
(3, 'Rahul Mehta', 'rahul.mehta@airportsystem.com', '9823456789'),
(4, 'Neha Singh', 'neha.singh@airportsystem.com', '9811123456'),
(5, 'Sanjay Patel', 'sanjay.patel@airportsystem.com', '9856781234'),
(6, 'Ananya Das', 'ananya.das@airportsystem.com', '9845678912'),
(7, 'Ravi Kumar', 'ravi.kumar@airportsystem.com', '9870987654'),
(8, 'Sonal Gupta', 'sonal.gupta@airportsystem.com', '9812345678'),
(9, 'Deepak Chawla', 'deepak.chawla@airportsystem.com', '9823456712'),
(10, 'Megha Kapoor', 'megha.kapoor@airportsystem.com', '9867890123');






ALTER TABLE airport
DROP COLUMN AirportID;


ALTER TABLE airport
ADD PRIMARY KEY (IATA_Code);

-- SET SQL_SAFE_UPDATES = 0;  run this only if safe update issue arises bcoz of mysql
-- Step 1: Update Source
UPDATE Flight
JOIN Airport ON Flight.Source = Airport.Location
SET Flight.Source = Airport.IATA_Code;

-- Step 2: Update Destination
UPDATE Flight
JOIN Airport ON Flight.Destination = Airport.Location
SET Flight.Destination = Airport.IATA_Code;

ALTER TABLE Flight
CHANGE COLUMN Source SourceIATA VARCHAR(3),
CHANGE COLUMN Destination DestinationIATA VARCHAR(3);

ALTER TABLE Flight
ADD CONSTRAINT fk_source FOREIGN KEY (SourceIATA) REFERENCES Airport(IATA_Code),
ADD CONSTRAINT fk_destination FOREIGN KEY (DestinationIATA) REFERENCES Airport(IATA_Code);

-- SET SQL_SAFE_UPDATES = 1; run this only if safe update issue arised then do this to undo

ALTER TABLE payments
DROP COLUMN PaymentMethod,
DROP COLUMN TransactionID;


CREATE TABLE AdminActions(
    ActionID INT AUTO_INCREMENT PRIMARY KEY,
    AdminID BIGINT UNSIGNED,
    ActionType ENUM('Add Flight', 'Delete Flight', 'Approve Request', 'Deny Request') NOT NULL,
    FlightID BIGINT UNSIGNED,
    RequestID BIGINT UNSIGNED,
    ActionTime DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (AdminID) REFERENCES Admin(AdminID),
    FOREIGN KEY (FlightID) REFERENCES Flight(FlightID) ON DELETE SET NULL,
    FOREIGN KEY (RequestID) REFERENCES SpecialRequests(RequestID)
);