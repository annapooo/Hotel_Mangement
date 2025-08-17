import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("mysql_pass"),
            database="hotelManagement"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None  # Explicitly return None for error case

def check_password(stored_password, password):
    """Checks if the provided password matches the stored password."""
    return stored_password == password

def login(username, password, table_name):
    """
    Handles user login.

    Args:
        username (str): The username entered by the user.
        password (str): The password entered by the user.
        table_name (str): The name of the table to query (e.g., "employee" or "guests").

    Returns:
        tuple: (True, user_data) if login is successful, (False, None) otherwise.
    """
    connection = get_db_connection()
    if connection is None:
        return False, None  # Exit if connection failed

    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name} WHERE Username = %s", (username,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        user = None  # Ensure user is None in case of query error
    finally:
        connection.close()

    if user and check_password(user[5], password):
        return True, user
    return False, None



def employee_login(username, password):
    """Logs in an employee."""
    return login(username, password, "employee")

def guest_login(username, password):
    """Logs in a guest."""
    return login(username, password, "guest")

def register_guest(username, password, name, email, phone):
    """Registers a new guest in the database."""
    connection = get_db_connection()
    if connection is None:
        raise Exception("Failed to connect to the database")

    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO guest (Username, Password, firstName, Email, phoneNo) VALUES (%s, %s, %s, %s, %s)",
            (username, password, name, email, phone),
        )
        connection.commit()
    except mysql.connector.Error as err:
        connection.rollback()
        raise Exception(f"Error registering guest: {err}")  # Wrap the error for consistent handling
    finally:
        connection.close()



def book_room(guest_id, selected_room, checkin_date, checkout_date,tamt):
    """Books a room for a guest."""
    connection = get_db_connection()
    if connection is None:
        raise Exception("Failed to connect to the database")

    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO Reservation (GuestID, RoomID, CheckInDate, CheckOutDate,ReservationStatus,totalAmount) VALUES (%s, %s, %s, %s, 'Confirmed',%s)",
            (guest_id, selected_room, checkin_date, checkout_date,tamt)
        )
        cursor.execute("UPDATE Room SET RoomStatus = 'Occupied' WHERE RoomID = %s", (selected_room,))
        connection.commit()
    except mysql.connector.Error as err:
        connection.rollback()
        raise Exception(f"Error booking room: {err}. guest_id={guest_id}, selected_room={selected_room}, checkin_date={checkin_date}, checkout_date={checkout_date}")
    finally:
        connection.close()


def order_food(guest_id, selected_item, quantity, total_price):
    """Places a food order for a guest."""
    connection = get_db_connection()
    if connection is None:
        raise Exception("Failed to connect to the database")

    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO RestaurantOrders (GuestID, ItemOrdered, Quantity, TotalPrice, OrderStatus) VALUES (%s, %s, %s, %s, 'Completed')",
            (guest_id, selected_item, quantity, total_price),
        )
        connection.commit()
    except mysql.connector.Error as err:
        connection.rollback()
        raise Exception(f"Error ordering food: {err}")
    finally:
        connection.close()



def view_bill(guest_id):
    """Retrieves billing information for a guest."""
    connection = get_db_connection()
    if connection is None:
        raise Exception("Failed to connect to the database")

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT BillID, AmountDue, AmountPaid, PaymentStatus FROM Billing WHERE ReservationID IN (SELECT ReservationID FROM Reservation WHERE GuestID = %s)",
            (guest_id,),
        )
        bill_data = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching bill: {err}")
        bill_data = [] # Return empty list
    finally:
        connection.close()
    return bill_data