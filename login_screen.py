import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv("mysql_pass"),
    'database': 'hotelManagement'
}

class LoginScreen(tk.Toplevel):
    def __init__(self, master, on_guest_login=None, on_employee_login=None, on_guest_register=None):
        super().__init__(master)
        self.title("Login")
        self.geometry('300x200')
        self.on_guest_login = on_guest_login
        self.on_employee_login = on_employee_login
        self.on_guest_register = on_guest_register

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        ttk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.register_button = ttk.Button(self, text="Register", command=self.register)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.user_type = tk.StringVar()
        self.user_type.set("guest")
        guest_radio = ttk.Radiobutton(self, text="Guest", variable=self.user_type, value="guest")
        employee_radio = ttk.Radiobutton(self, text="Employee", variable=self.user_type, value="employee")
        guest_radio.grid(row=4, column=0, padx=10, pady=5, sticky='w')
        employee_radio.grid(row=4, column=1, padx=10, pady=5, sticky='e')

        self.grid_columnconfigure(1, weight=1)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get()

        try:
            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()

            if user_type == "guest":
                query = "SELECT * FROM guest WHERE username = %s AND password = %s"
                mycursor.execute(query, (username, password))
                user = mycursor.fetchone()
                if user:
                    self.on_guest_login(username)
                else:
                    messagebox.showerror("Login Error", "Invalid username or password for guest.")
            elif user_type == "employee":
                query = "SELECT * FROM employee WHERE username = %s AND password = %s"
                mycursor.execute(query, (username, password))
                user = mycursor.fetchone()
                if user:
                    role = user[3]
                    self.on_employee_login(username, role)
                else:
                    messagebox.showerror("Login Error", "Invalid username or password for employee.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error logging in: {err}")
        finally:
            if mydb and mydb.is_connected():
                mycursor.close()
                mydb.close()

    def register(self):
        if self.on_guest_register:
            self.on_guest_register()
        else:
            messagebox.showerror("Error", "Registration functionality not linked.")