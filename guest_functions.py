# guest_functions.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
# from tkcalendar import Calendar  # Removed Calendar import

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv("mysql_pass"),
    'database': 'hotelManagement'
}

class GuestFunctions:
    def __init__(self, master, logged_in_guest_username=None):
        self.master = master
        self.logged_in_guest_username = logged_in_guest_username
        self.available_rooms_list = None
        self.checkin_date_entry = None  #  Now an Entry again
        self.checkout_date_entry = None  # Now an Entry again
        self.my_reservations_list = None
        self.restaurant_tab = None
        self.menu_list = None
        self.quantity_entry = None
        self.order_list = None
        self.current_order = []
        self.checkin_calendar = None  # Removed Calendar widgets
        self.checkout_calendar = None

    def create_guest_tab(self, guest_tab):
        if self.logged_in_guest_username:
            try:
                mydb = mysql.connector.connect(**DB_CONFIG)
                mycursor = mydb.cursor()
                query = "SELECT Name, email, phoneNo FROM guest WHERE username = %s"
                mycursor.execute(query, (self.logged_in_guest_username,))
                guest_data = mycursor.fetchone()
                if guest_data:
                    name, email, phone = guest_data
                    ttk.Label(guest_tab, text=f"Welcome, {name}!").pack(pady=10)
                    ttk.Label(guest_tab, text=f"Email: {email}").pack(pady=5)
                    ttk.ttk.Label(guest_tab, text=f"Phone: {phone}").pack(pady=5)
                else:
                    ttk.Label(guest_tab, text="Guest information not found.").pack(pady=10)
            except mysql.connector.Error as err:
                ttk.Label(guest_tab, text=f"Database Error: {err}").pack(pady=10)
            finally:
                if mydb and mydb.is_connected():
                    mycursor.close()
                    mydb.close()
        else:
            ttk.Label(guest_tab, text="Not logged in as a guest.").pack(pady=10)

    def create_rooms_tab(self, rooms_tab):
        ttk.Label(rooms_tab, text="Check-in Date:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        # Use Entry widget
        self.checkin_date_entry = ttk.Entry(rooms_tab)
        self.checkin_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')


        ttk.Label(rooms_tab, text="Check-out Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.checkout_date_entry = ttk.Entry(rooms_tab)
        self.checkout_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.available_rooms_list = tk.Listbox(rooms_tab, width=70)
        self.available_rooms_list.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        search_button = ttk.Button(rooms_tab, text="Check Availability", command=self.check_room_availability)
        search_button.grid(row=3, column=0, columnspan=3, pady=10)

        book_button = ttk.Button(rooms_tab, text="Book Selected Room", command=self.book_selected_room)
        book_button.grid(row=4, column=0, columnspan=3, pady=5)

    def check_room_availability(self):
        # Get selected date from Entry
        checkin_date = self.checkin_date_entry.get()
        checkout_date = self.checkout_date_entry.get()


        self.available_rooms_list.delete(0, tk.END)

        try:
            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()
            query = """
            SELECT r.roomId, r.roomNumber, r.roomType, r.PricePerNight
            FROM room r
            WHERE r.roomStatus = 'Available'
            AND r.roomId NOT IN (
                SELECT res.roomId
                FROM reservation res
                WHERE (res.checkInDate <= %s AND res.checkOutDate >= %s)
                   OR (res.checkInDate <= %s AND res.checkOutDate >= %s)
                   OR (res.checkInDate >= %s AND res.checkOutDate <= %s)
            )
            """
            mycursor.execute(query, (checkout_date, checkin_date, checkin_date, checkout_date, checkin_date, checkout_date))
            available_rooms = mycursor.fetchall()

            if available_rooms:
                for room in available_rooms:
                    self.available_rooms_list.insert(tk.END, f"ID: {room[0]}, Number: {room[1]}, Type: {room[2]}, Price: {room[3]}")
            else:
                self.available_rooms_list.insert(tk.END, "No rooms available for the selected dates.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error checking availability: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    def book_selected_room(self):
        selected_room_index = self.available_rooms_list.curselection()
        # Get date from Entry
        checkin_date = self.checkin_date_entry.get()
        checkout_date = self.checkout_date_entry.get()
        if not selected_room_index:
            messagebox.showerror("Booking Error", "Please select a room to book.")
            return

        if not self.logged_in_guest_username:
            messagebox.showerror("Booking Error", "You must be logged in to make a reservation.")
            return

        try:
            selected_room_info = self.available_rooms_list.get(selected_room_index[0])
            room_id = selected_room_info.split(',')[0].split(': ')[1]

            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()

            query_price = "SELECT PricePerNight FROM room WHERE roomId = %s"
            mycursor.execute(query_price, (room_id,))
            price_result = mycursor.fetchone()
            if not price_result:
                messagebox.showerror("Booking Error", "Could not retrieve room price.")
                return
            price_per_night = price_result[0]

            date_format = "%Y-%m-%d"
            # Format the dates from the Entry
            checkin = datetime.strptime(checkin_date, date_format).date()
            checkout = datetime.strptime(checkout_date, date_format).date()
            number_of_nights = (checkout - checkin).days
            total_amount = price_per_night * number_of_nights

            query_insert = """
            INSERT INTO reservation (guestId, roomId, checkInDate, checkOutDate, TotalAmount, reservationStatus)
            SELECT g.guestId, %s, %s, %s, %s, 'Confirmed'
            FROM guest g
            WHERE g.username = %s
            """
            mycursor.execute(query_insert, (room_id, checkin, checkout, total_amount, self.logged_in_guest_username))
            mydb.commit()
            messagebox.showinfo("Booking Successful", f"Room booked successfully! Total amount: {total_amount:.2f}")
            self.check_room_availability()
        except mysql.connector.Error as err:
            mydb.rollback()
            messagebox.showerror("Booking Error", f"Error booking room: {err}")
        except ValueError:
            messagebox.showerror("Booking Error", "Invalid date format. Please use YYYY-MM-DD.")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    def create_reservations_tab(self, reservations_tab):
        ttk.Label(reservations_tab, text="Your Upcoming Reservations:").pack(pady=10)
        self.my_reservations_list = tk.Listbox(reservations_tab, width=70)
        self.my_reservations_list.pack(pady=5)

        ttk.Button(reservations_tab, text="Cancel Selected Reservation", command=self.cancel_selected_reservation).pack(pady=5)
        ttk.Button(reservations_tab, text="View Bill & Pay", command=self.view_bill_and_pay).pack(pady=5) # Button to view bill

        self.load_guest_reservations()

    def load_guest_reservations(self):
        self.my_reservations_list.delete(0, tk.END)
        if self.logged_in_guest_username:
            try:
                mydb = mysql.connector.connect(**DB_CONFIG)
                mycursor = mydb.cursor()
                query = """
                SELECT res.reservationId, r.roomNumber, res.checkInDate, res.checkOutDate, res.TotalAmount, res.reservationStatus
                FROM reservation res
                JOIN room r ON res.roomId = r.roomId
                JOIN guest g ON res.guestId = g.guestId
                WHERE g.username = %s
                AND res.checkOutDate >= CURDATE()
                """
                mycursor.execute(query, (self.logged_in_guest_username,))
                reservations = mycursor.fetchall()
                if reservations:
                    for res in reservations:
                        self.my_reservations_list.insert(tk.END, f"ID: {res[0]}, Room: {res[1]}, Check-in: {res[2]}, Check-out: {res[3]}, Total: {res[4]:.2f}, Status: {res[5]}")
                else:
                    self.my_reservations_list.insert(tk.END, "No upcoming reservations found.")
            except mysql.connector.Error as err:
                self.my_reservations_list.insert(tk.END, f"Database Error: {err}")
            finally:
                if mydb and mydb.is_connected():
                    mycursor.close()
                    mydb.close()
        else:
            self.my_reservations_list.insert(tk.END, "Not logged in as a guest.")

    def cancel_selected_reservation(self):
        selected_reservation_index = self.my_reservations_list.curselection()
        if not selected_reservation_index:
            messagebox.showerror("Cancellation Error", "Please select a reservation to cancel.")
            return

        if not self.logged_in_guest_username:
            messagebox.showerror("Cancellation Error", "You must be logged in to cancel a reservation.")
            return

        try:
            selected_reservation_info = self.my_reservations_list.get(selected_reservation_index[0])
            reservation_id = selected_reservation_info.split(',')[0].split(': ')[1]

            confirm_cancel = messagebox.askyesno("Confirm Cancellation", f"Are you sure you want to cancel reservation ID: {reservation_id}?")
            if confirm_cancel:
                mydb = mysql.connector.connect(**DB_CONFIG)
                mycursor = mydb.cursor()
                query = "UPDATE reservation SET reservationStatus = 'Canceled' WHERE reservationId = %s AND guestId = (SELECT guestId FROM guest WHERE username = %s)"
                mycursor.execute(query, (reservation_id, self.logged_in_guest_username))
                mydb.commit()
                if mycursor.rowcount > 0:
                    messagebox.showinfo("Cancellation Successful", f"Reservation ID: {reservation_id} has been canceled.")
                    self.load_guest_reservations()
                    self.check_room_availability()
                else:
                    messagebox.showerror("Cancellation Error", f"Could not cancel reservation ID: {reservation_id}. Please ensure it belongs to your account.")
        except mysql.connector.Error as err:
            mydb.rollback()
            messagebox.showerror("Database Error", f"Error canceling reservation: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    def create_restaurant_tab(self, restaurant_tab):
        self.restaurant_tab = restaurant_tab
        self.menu_list = tk.Listbox(restaurant_tab, width=60)
        self.menu_list.grid(row=0, column=0, padx=5, pady=5)

        ttk.Label(restaurant_tab, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.quantity_entry = ttk.Entry(restaurant_tab, width=10)
        self.quantity_entry.grid(row=1, column=0, padx=80, pady=5, sticky='w')

        ttk.Button(restaurant_tab, text="Add to Order", command=self.add_to_order).grid(row=2, column=0, pady=5)

        ttk.Label(restaurant_tab, text="Your Order:").grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.order_list = tk.Listbox(restaurant_tab, width=40)
        self.order_list.grid(row=1, column=1, rowspan=2, padx=5, pady=5)

        ttk.Button(restaurant_tab, text="Place Order", command=self.place_restaurant_order).grid(row=3, column=1, pady=5)

        self.load_restaurant_menu()

    def load_restaurant_menu(self):
        self.menu_list.delete(0, tk.END)
        try:
            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()
            query = "SELECT MenuItemID, ItemName, Category, Price FROM RestaurantMenu"
            mycursor.execute(query)
            menu_items = mycursor.fetchall()
            if menu_items:
                for item in menu_items:
                    self.menu_list.insert(tk.END, f"[{item[0]}] {item[1]} ({item[2]}) - ₹{item[3]:.2f}")
            else:
                self.menu_list.insert(tk.END, "Restaurant menu is empty.")
        except mysql.connector.Error as err:
            self.menu_list.insert(tk.END, f"Database Error: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    def add_to_order(self):
        selected_menu_index = self.menu_list.curselection()
        quantity_str = self.quantity_entry.get()
        if not selected_menu_index:
            messagebox.showerror("Order Error", "Please select an item from the menu.")
            return
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("Order Error", "Quantity must be greater than zero.")
                return
            selected_item_info = self.menu_list.get(selected_menu_index[0])
            item_id = selected_item_info.split('[')[1].split(']')[0]
            item_name = selected_item_info.split('] ')[1].split(' (')[0]
            price_str = selected_item_info.split('₹')[1]
            price = float(price_str)
            self.current_order.append({'item_id': item_id, 'item_name': item_name, 'quantity': quantity, 'price': price})
            self.update_order_list()
            self.quantity_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Order Error", "Invalid quantity.")

    def update_order_list(self):
        self.order_list.delete(0, tk.END)
        for item in self.current_order:
            self.order_list.insert(tk.END, f"{item['item_name']} x {item['quantity']} - ₹{item['price'] * item['quantity']:.2f}")

    def place_restaurant_order(self):
        if not self.current_order:
            messagebox.showinfo("Order Info", "Your order is empty.")
            return
        if not self.logged_in_guest_username:
            messagebox.showerror("Order Error", "You must be logged in to place an order.")
            return

        try:
            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()
            guest_query = "SELECT guestId, roomId FROM reservation WHERE guestId = (SELECT guestId FROM guest WHERE username = %s) AND checkOutDate >= CURDATE() ORDER BY checkInDate LIMIT 1"
            mycursor.execute(guest_query, (self.logged_in_guest_username,))
            guest_reservation_data = mycursor.fetchone()

            if not guest_reservation_data:
                messagebox.showerror("Order Error", "You must have an active reservation to place a restaurant order.")
                return

            guest_id = guest_reservation_data[0]
            room_id = guest_reservation_data[1]

            order_query = "INSERT INTO FoodOrder (guestId, roomId, orderDate, orderStatus) VALUES (%s, %s, CURDATE(), 'Placed')"
            mycursor.execute(order_query, (guest_id, room_id))
            order_id = mycursor.lastrowid

            for item in self.current_order:
                order_item_query = "INSERT INTO OrderItem (orderId, menuItemId, quantity) VALUES (%s, %s, %s)"
                mycursor.execute(order_item_query, (order_id, item['item_id'], item['quantity']))

            mydb.commit()
            messagebox.showinfo("Order Placed", "Your order has been placed successfully!")
            self.current_order = []
            self.update_order_list()
        except mysql.connector.Error as err:
            mydb.rollback()
            messagebox.showerror("Database Error", f"Error placing order: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    def view_bill_and_pay(self):
        selected_reservation_index = self.my_reservations_list.curselection()
        if not selected_reservation_index:
            messagebox.showerror("Payment Error", "Please select a reservation to view the bill.")
            return

        if not self.logged_in_guest_username:
            messagebox.showerror("Payment Error", "You must be logged in to view your bill.")
            return

        try:
            selected_reservation_info = self.my_reservations_list.get(selected_reservation_index[0])
            reservation_id = selected_reservation_info.split(',')[0].split(': ')[1]

            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()
            # Get reservation details
            query = """
                SELECT res.TotalAmount
                FROM reservation res
                WHERE res.reservationId = %s AND res.guestId = (SELECT guestId FROM guest WHERE username = %s)
                """
            mycursor.execute(query, (reservation_id, self.logged_in_guest_username))
            reservation_data = mycursor.fetchone()

            if not reservation_data:
                messagebox.showerror("Payment Error", "Reservation not found or does not belong to this guest.")
                return

            total_amount = reservation_data[0]

            # Get any food order totals for the reservation
            food_order_query = """
                SELECT SUM(rm.Price * oi.quantity) AS food_total
                FROM FoodOrder fo
                JOIN OrderItem oi ON fo.orderId = oi.orderId
                JOIN RestaurantMenu rm ON oi.menuItemId = rm.MenuItemID
                WHERE fo.roomId = (SELECT roomId FROM reservation WHERE reservationId = %s)
                """
            mycursor.execute(food_order_query, (reservation_id,))
            food_total_data = mycursor.fetchone()
            food_total = food_total_data[0] if food_total_data[0] else 0.0
            final_bill = total_amount + food_total
            messagebox.showinfo("Your Bill", f"Total Amount Due: ₹{final_bill:.2f}")

            # Simulate Payment
            payment_result = messagebox.askyesno("Proceed to Payment", f"Do you want to pay ₹{final_bill:.2f} now?")
            if payment_result:
                # In a real application, you would integrate with a payment gateway here
                # For this example, we'll just update the reservation status to 'Paid'
                update_payment_status_query = "UPDATE reservation SET reservationStatus = 'Paid' WHERE reservationId = %s AND guestId = (SELECT guestId FROM guest WHERE username = %s)"
                mycursor.execute(update_payment_status_query, (reservation_id, self.logged_in_guest_username))
                mydb.commit()
                messagebox.showinfo("Payment Successful", "Payment processed successfully.  Reservation status updated.")
                self.load_guest_reservations()  # Refresh the reservation list
            else:
                messagebox.showinfo("Payment Canceled", "Payment canceled.")

        except mysql.connector.Error as err:
            mydb.rollback()
            messagebox.showerror("Database Error", f"Error processing payment: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()
