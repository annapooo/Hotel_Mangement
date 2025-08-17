# main_hotel_app.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from login_screen import LoginScreen
from guest_functions import GuestFunctions
from guest_dashboard import GuestDashboard
import os

class HotelFrontend(tk.Tk):
    def __init__(self, logged_in_guest_username):
        super().__init__()
        self.title("Hotel Management")
        self.logged_in_guest_username = logged_in_guest_username
        self.guest_functions = GuestFunctions(self, logged_in_guest_username)

        self.notebook = ttk.Notebook(self)
        self.guest_tab = ttk.Frame(self.notebook)
        self.rooms_tab = ttk.Frame(self.notebook)
        self.reservations_tab = ttk.Frame(self.notebook)
        self.restaurant_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.guest_tab, text='Guest Profile')
        self.notebook.add(self.rooms_tab, text='Book Rooms')
        self.notebook.add(self.reservations_tab, text='My Reservations')
        self.notebook.add(self.restaurant_tab, text='Restaurant Order')

        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')

        self.create_tabs()
        self.withdraw() # Hide the main window initially

    def create_tabs(self):
        self.guest_functions.create_guest_tab(self.guest_tab)
        self.guest_functions.create_rooms_tab(self.rooms_tab)
        self.guest_functions.create_reservations_tab(self.reservations_tab)
        self.guest_functions.create_restaurant_tab(self.restaurant_tab)

    def show_rooms_tab(self):
        self.notebook.select(self.rooms_tab)

    def show_reservations_tab(self):
        self.notebook.select(self.reservations_tab)
        self.guest_functions.load_guest_reservations()

    def show_restaurant_tab(self):
        self.notebook.select(self.restaurant_tab)

    def show_guest_tab(self):
        self.notebook.select(self.guest_tab)
        self.guest_functions.create_guest_tab(self.guest_tab)

def main():
    root = tk.Tk()
    login_window = tk.Toplevel(root)
    main_app = None # Initialize main_app

    def on_guest_login_success(username):
        nonlocal main_app
        login_window.destroy()
        main_app = HotelFrontend(username)
        dashboard_window = tk.Toplevel(root)
        guest_dashboard = GuestDashboard(dashboard_window, username, main_app)
        root.withdraw()

    def on_employee_login_success(username, role):
        messagebox.showinfo("Employee Login", f"Employee '{username}' logged in with role: {role} (Functionality not implemented)")
        login_window.destroy()
        # Here you would open the employee-specific interface

    def open_registration_form():
        registration_window = tk.Toplevel(root)
        registration_window.title("Guest Registration")
        # ... (Your guest registration form UI code) ...
        tk.Label(registration_window, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_entry = tk.Entry(registration_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(registration_window, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        username_entry = tk.Entry(registration_window)
        username_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(registration_window, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        password_entry = tk.Entry(registration_window, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(registration_window, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        email_entry = tk.Entry(registration_window)
        email_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(registration_window, text="Phone No:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        phone_entry = tk.Entry(registration_window)
        phone_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        register_button = tk.Button(registration_window, text="Register", command=lambda: register_new_guest(
            name_entry.get(), username_entry.get(), password_entry.get(), email_entry.get(), phone_entry.get(), registration_window
        ))
        register_button.grid(row=5, column=0, columnspan=2, pady=10)

    def register_new_guest(name, username, password, email, phone, registration_window):
        try:
            import mysql.connector
            from dotenv import load_dotenv
            load_dotenv()
            DB_CONFIG = {
                'host': 'localhost',
                'user': 'root',
                'password': os.getenv("mysql_pass"),
                'database': 'hotelManagement'
            }
            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()
            query = "INSERT INTO guest (Name, username, password, email, phoneNo) VALUES (%s, %s, %s, %s, %s)"
            values = (name, username, password, email, phone)
            mycursor.execute(query, values)
            mydb.commit()
            messagebox.showinfo("Registration Successful", f"Guest '{name}' registered successfully.")
            registration_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error registering guest: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    login_screen = LoginScreen(login_window, on_guest_login=on_guest_login_success,
                               on_employee_login=on_employee_login_success,
                               on_guest_register=open_registration_form)
    root.withdraw()
    login_window.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

if __name__ == "__main__":
    main()