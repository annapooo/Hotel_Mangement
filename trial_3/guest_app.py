import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import mysql.connector
import os
from dotenv import load_dotenv  # Import dotenv to load the .env file

# Load environment variables from .env file
load_dotenv()

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv("mysql_pass"),  # Getting password from the environment variable
    'database': 'hotelManagement'
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

class GuestApp:
    def __init__(self, master, guest_id):
        self.master = master
        self.guest_id = guest_id
        self.master.title("Guest Dashboard")
        self.master.geometry("600x400")
        self.main_frame = tk.Frame(self.master, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)
        self.load_dashboard()
    def load_dashboard(self):
        # Clear existing widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Header Frame
        header_frame = tk.Frame(self.main_frame, pady=10)
        header_frame.pack(fill="x")
        header_label = tk.Label(header_frame, text=f"Welcome Guest ID: {self.guest_id}", font=("Helvetica", 16, "bold"))
        header_label.pack()

        # Dashboard Frame
        dashboard_frame = tk.LabelFrame(self.main_frame, text="Guest Actions", padx=20, pady=20, font=("Helvetica", 12, "bold"))
        dashboard_frame.pack(pady=20, fill="both", expand=True)

        buttons = [
            ("🏨 View Available Rooms", self.view_rooms),
            ("📅 Make Reservation", self.make_reservation),
            ("🧹 Request Services", self.request_services),
            ("🍽️ Restaurant Order", self.restaurant_order),
            ("📝 Provide Feedback", self.provide_feedback),
            ("📋 Show Reservations", self.show_reservations)
        ]

        for i, (label, command) in enumerate(buttons):
            btn = tk.Button(dashboard_frame, text=label, font=("Arial", 12), width=30, height=2, bg="#4CAF50", fg="white", activebackground="#45a049", relief="raised", command=command)
            btn.grid(row=i, column=0, pady=8)

    def view_rooms(self):
        self.popup_window("Available Rooms", "SELECT * FROM room WHERE roomStatus = 'Available'")

    def make_reservation(self):
        window = tk.Toplevel(self.master)
        window.title("Make Reservation")

        # Frame for form
        form_frame = tk.Frame(window, padx=20, pady=20)
        form_frame.pack(padx=10, pady=10)

        # Room Number
        tk.Label(form_frame, text="Room Number").grid(row=0, column=0, sticky="w", pady=5)
        room_entry = tk.Entry(form_frame)
        room_entry.grid(row=0, column=1, pady=5)

        # Check-in Date
        tk.Label(form_frame, text="Check-in Date").grid(row=1, column=0, sticky="w", pady=5)
        check_in = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        check_in.grid(row=1, column=1, pady=5)

        # Check-out Date
        tk.Label(form_frame, text="Check-out Date").grid(row=2, column=0, sticky="w", pady=5)
        check_out = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        check_out.grid(row=2, column=1, pady=5)

        # Amount Paying Now
        tk.Label(form_frame, text="Amount Paying Now").grid(row=3, column=0, sticky="w", pady=5)
        amount_paid_entry = tk.Entry(form_frame)
        amount_paid_entry.grid(row=3, column=1, pady=5)

        # Payment Method
        tk.Label(form_frame, text="Payment Method").grid(row=4, column=0, sticky="w", pady=5)
        payment_method_var = tk.StringVar(window)
        payment_method_var.set("Cash")
        tk.OptionMenu(form_frame, payment_method_var, "Cash", "Credit Card", "Online Payment").grid(row=4, column=1, pady=5)

        # Reserve button
        def reserve():
            db = connect_db()
            cursor = db.cursor()
            try:
                cursor.execute("SELECT roomId, PricePerNight FROM room WHERE roomNumber = %s AND roomStatus = 'Available'", (room_entry.get(),))
                room = cursor.fetchone()

                if room:
                    room_id, price = room
                    nights = (check_out.get_date() - check_in.get_date()).days
                    total = price * nights

                    cursor.execute("""
                        INSERT INTO reservation (guestId, roomId, checkInDate, checkOutDate, TotalAmount, reservationStatus)
                        VALUES (%s, %s, %s, %s, %s, 'Confirmed')
                    """, (self.guest_id, room_id, check_in.get_date(), check_out.get_date(), total))
                    db.commit()
                    reservation_id = cursor.lastrowid

                    cursor.execute("UPDATE room SET roomStatus = 'Occupied' WHERE roomId = %s", (room_id,))
                    db.commit()

                    amount_paid = float(amount_paid_entry.get())
                    payment_method = payment_method_var.get()

                    # Create billing for the reservation
                    self.create_billing_for_reservation(reservation_id, total, amount_paid, payment_method)

                    messagebox.showinfo("Success", "Room Reserved and Billing Created!")
                else:
                    messagebox.showerror("Error", "Room not available.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()

        tk.Button(form_frame, text="Reserve", command=reserve).grid(row=5, columnspan=2, pady=10)

    def create_billing_for_reservation(self, reservation_id, amount_due, amount_paid=0, payment_method="Cash"):
        db = connect_db()
        cursor = db.cursor()

        if amount_paid == 0:
            payment_status = "Pending"
        elif amount_paid < amount_due:
            payment_status = "Partially Paid"
        else:
            payment_status = "Paid"

        try:
            cursor.execute("""
                INSERT INTO billing (reservationId, AmountDue, AmountPaid, PaymentStatus, PaymentMethod, ApprovalStatus)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (reservation_id, amount_due, amount_paid, payment_status, payment_method, "Pending"))
            db.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create billing: {e}")
        finally:
            db.close()

    def request_services(self):
        window = tk.Toplevel(self.master)
        window.title("Request Services")

        # Frame for form
        form_frame = tk.Frame(window, padx=20, pady=20)
        form_frame.pack(padx=10, pady=10)

        # Service Type
        tk.Label(form_frame, text="Service Type").grid(row=0, column=0, sticky="w", pady=5)
        service_type = tk.StringVar()
        tk.OptionMenu(form_frame, service_type, "Room Cleaning", "Food Delivery", "Laundry").grid(row=0, column=1, pady=5)

        # Description
        tk.Label(form_frame, text="Description").grid(row=1, column=0, sticky="w", pady=5)
        description = tk.Entry(form_frame, width=40)
        description.grid(row=1, column=1, pady=5)

        def submit_service():
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO housekeepingmaintenance (RoomID, TaskDescription, TaskStatus, AssignedEmployeeID) VALUES (NULL, %s, 'Pending', NULL)", (description.get(),))
            db.commit()
            db.close()
            messagebox.showinfo("Submitted", "Request submitted.")

        tk.Button(form_frame, text="Submit", command=submit_service).grid(row=2, columnspan=2, pady=10)

    def restaurant_order(self):
        window = tk.Toplevel(self.master)
        window.title("Restaurant Order")

        # Connect to the database and fetch the menu
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MenuItemID, ItemName, Price FROM restaurantmenu")
            menu_items = cursor.fetchall()  # Fetch all menu items
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch menu: {e}")
            db.close()
            return

        db.close()

        # Create a dropdown menu for selecting items
        tk.Label(window, text="Select Menu Item").grid(row=0, column=0, sticky="w", pady=5)
        selected_item = tk.StringVar(window)
        selected_item.set("Select an item")  # Default value

        # Create a dictionary to map item names to their details
        menu_dict = {f"{item[1]} (${item[2]:.2f})": item for item in menu_items}
        item_names = list(menu_dict.keys())

        menu_dropdown = tk.OptionMenu(window, selected_item, *item_names)
        menu_dropdown.grid(row=0, column=1, pady=5)

        tk.Label(window, text="Quantity").grid(row=1, column=0, sticky="w", pady=5)
        quantity_entry = tk.Entry(window, width=5)
        quantity_entry.grid(row=1, column=1, pady=5)

        def place_order():
            item_name = selected_item.get()
            if item_name == "Select an item":
                messagebox.showerror("Error", "Please select a menu item.")
                return

            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.")
                return

            # Get the selected item's details
            menu_item_id, item_name, price = menu_dict[item_name]
            total_price = price * quantity

            # Insert the order into the database
            db = connect_db()
            cursor = db.cursor()
            try:
                cursor.execute(
                    "INSERT INTO restaurantorders (GuestID, ItemOrdered, Quantity, TotalPrice, OrderStatus) "
                    "VALUES (%s, %s, %s, %s, 'Pending')",  # Use 'Pending' as the default status
                    (self.guest_id, item_name, quantity, total_price)
                )
                db.commit()

                messagebox.showinfo("Success", f"Order placed! Total Price: ${total_price:.2f}")
                window.destroy()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Failed to place order: {e}")
            finally:
                db.close()

        tk.Button(window, text="Place Order", command=place_order).grid(row=2, columnspan=2, pady=10)

    def provide_feedback(self):
        window = tk.Toplevel(self.master)
        window.title("Feedback")

        # Frame for form
        form_frame = tk.Frame(window, padx=20, pady=20)
        form_frame.pack(padx=10, pady=10)

        tk.Label(form_frame, text="Rating (1 to 5)").grid(row=0, column=0, sticky="w", pady=5)
        rating = tk.Entry(form_frame)
        rating.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Comments").grid(row=1, column=0, sticky="w", pady=5)
        comments = tk.Entry(form_frame, width=40)
        comments.grid(row=1, column=1, pady=5)

        def submit_feedback():
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO feedback (guestId, rating, comments) VALUES (%s, %s, %s)", (self.guest_id, rating.get(), comments.get()))
            db.commit()
            db.close()
            messagebox.showinfo("Thank You", "Feedback submitted!")

        tk.Button(form_frame, text="Submit", command=submit_feedback).grid(row=2, columnspan=2, pady=10)

    def popup_window(self, title, query):
        window = tk.Toplevel(self.master)
        window.title(title)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            tk.Label(window, text=str(result)).pack(pady=5)
        db.close()

    def show_reservations(self):
        window = tk.Toplevel(self.master)
        window.title("Your Reservations")

        db = connect_db()
        cursor = db.cursor()

        # Query to fetch reservations for the logged-in guest
        query = """
            SELECT reservationId, roomId, checkInDate, checkOutDate, TotalAmount, reservationStatus
            FROM reservation
            WHERE guestId = %s
        """
        cursor.execute(query, (self.guest_id,))
        reservations = cursor.fetchall()
        db.close()

        # Display reservations in the new window
        if reservations:
            for reservation in reservations:
                tk.Label(window, text=f"Reservation ID: {reservation[0]}, Room ID: {reservation[1]}, "
                                    f"Check-In: {reservation[2]}, Check-Out: {reservation[3]}, "
                                    f"Total Amount: {reservation[4]}, Status: {reservation[5]}").pack(pady=5)
        else:
            tk.Label(window, text="No reservations found.").pack(pady=5)

        tk.Button(window, text="Close", command=window.destroy).pack(pady=10)

