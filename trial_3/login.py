import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os
from dotenv import load_dotenv

from guest_app import GuestApp
from employee_app import EmployeeApp

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv("mysql_pass"),
    'database': 'hotelManagement'
}

def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Hotel Management Login")
        self.master.geometry("400x350")
        self.master.resizable(False, False)

        # Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f4f8")
        self.style.configure("TLabel", background="#f0f4f8", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#333", background="#f0f4f8")
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.configure("TEntry", padding=5)
        self.style.map("TButton", background=[("active", "#dbeafe")], foreground=[("active", "#000")])

        # Main frame
        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="Hotel Management System", style="Header.TLabel").pack(pady=10)

        # User type selection
        self.user_type = tk.StringVar()
        ttk.Label(main_frame, text="Login as:").pack(anchor="w", pady=(0, 2))
        self.user_type_combo = ttk.Combobox(main_frame, textvariable=self.user_type, state="readonly", width=30)
        self.user_type_combo['values'] = ("Guest", "Employee")
        self.user_type_combo.current(0)
        self.user_type_combo.pack(anchor="w", pady=(0, 10))

        # Username and password
        ttk.Label(main_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack()

        ttk.Label(main_frame, text="Password:").pack(anchor="w", pady=(10, 0))
        self.password_entry = ttk.Entry(main_frame, show="*", width=30)
        self.password_entry.pack()

        # Buttons
        ttk.Button(main_frame, text="Login", command=self.login).pack(pady=(15, 5))
        ttk.Button(main_frame, text="Register as Guest", command=self.register_guest).pack()

    def login(self):
        user_type = self.user_type.get().lower()
        username = self.username_entry.get()
        password = self.password_entry.get()

        db = connect_db()
        if not db:
            messagebox.showerror("Error", "Database connection failed.")
            return

        cursor = db.cursor()

        if user_type == "guest":
            cursor.execute("SELECT guestId FROM guest WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                self.master.withdraw()
                guest_id = user[0]
                guest_root = tk.Toplevel(self.master)
                GuestApp(guest_root, guest_id)
            else:
                messagebox.showerror("Error", "Invalid guest credentials.")

        elif user_type == "employee":
            cursor.execute("SELECT employeeId FROM employee WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                self.master.withdraw()
                employee_id = user[0]
                employee_root = tk.Toplevel(self.master)
                EmployeeApp(employee_root, employee_id)
            else:
                messagebox.showerror("Error", "Invalid employee credentials.")

        db.close()

    def register_guest(self):
        reg_win = tk.Toplevel(self.master)
        reg_win.title("Guest Registration")
        reg_win.geometry("400x350")
    

        reg_frame = ttk.Frame(reg_win, padding="20")
        reg_frame.pack(fill="both", expand=True)

        ttk.Label(reg_frame, text="Guest Registration", style="Header.TLabel").pack(pady=10)

        ttk.Label(reg_frame, text="Full Name:").pack(anchor="w")
        name_entry = ttk.Entry(reg_frame, width=30)
        name_entry.pack()

        ttk.Label(reg_frame, text="Email:").pack(anchor="w", pady=(5, 0))
        email_entry = ttk.Entry(reg_frame, width=30)
        email_entry.pack()

        ttk.Label(reg_frame, text="Username:").pack(anchor="w", pady=(5, 0))
        uname_entry = ttk.Entry(reg_frame, width=30)
        uname_entry.pack()

        ttk.Label(reg_frame, text="Password:").pack(anchor="w", pady=(5, 0))
        pwd_entry = ttk.Entry(reg_frame, show="*", width=30)
        pwd_entry.pack()

        ttk.Label(reg_frame, text="Phone Number:").pack(anchor="w", pady=(5, 0))
        ph_entry = ttk.Entry(reg_frame, width=30)
        ph_entry.pack()

        def register():
            db = connect_db()
            if not db:
                messagebox.showerror("Error", "Database connection failed.")
                return
            cursor = db.cursor()
            try:
                cursor.execute(
                    "INSERT INTO guest (Name, email, username, password, phoneno) VALUES (%s, %s, %s, %s, %s)",
                    (name_entry.get(), email_entry.get(), uname_entry.get(), pwd_entry.get(), ph_entry.get())
                )
                db.commit()
                messagebox.showinfo("Success", "Guest registered successfully!")
                reg_win.destroy()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            db.close()

        ttk.Button(reg_frame, text="Register", command=register).pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
