import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import os
from dotenv import load_dotenv  # Import dotenv to load the .env file
from tkinter import font

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
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

class EmployeeApp:
    def __init__(self, master, employee_id):
        self.master = master
        self.employee_id = employee_id
        self.master.title("Employee Dashboard")

        self.role = self.get_employee_role()
        self.main_frame = tk.Frame(self.master, bg="#f5f5f5")
        self.main_frame.pack(fill="both", expand=True)

        self.load_dashboard()

    def get_employee_role(self):
        db = connect_db()
        if db is None:
            return ""
        cursor = db.cursor()
        cursor.execute("SELECT Role FROM employee WHERE EmployeeID = %s", (self.employee_id,))
        role = cursor.fetchone()
        db.close()
        return role[0] if role else ""

    def load_dashboard(self):
        self.master.geometry("600x400")
        header_font = font.Font(family="Helvetica", size=16, weight="bold")
        button_font = font.Font(family="Arial", size=12)

        # Header Label
        tk.Label(self.main_frame, text=f"Welcome Employee ID: {self.employee_id} | Role: {self.role}", font=header_font, bg="#f5f5f5").pack(pady=20)

        # Buttons with styling
        if self.role.lower() in ['manager', 'receptionist']:
            self.create_button("Manage Reservations", self.view_reservations, button_font, "#4CAF50")
            self.create_button("Manage Room Status", self.manage_room_status, button_font, "#008CBA")

        if self.role.lower() in ['housekeeper', 'manager']:
            self.create_button("Housekeeping Tasks", self.view_housekeeping_tasks, button_font, "#FF9800")

        if self.role.lower() == 'manager':
            self.create_button("Inventory", self.manage_inventory, button_font, "#9C27B0")
            self.create_button("Billing Approval", self.billing_approval, button_font, "#F44336")

        self.create_button("Restaurant Orders", self.view_restaurant_orders, button_font, "#FFC107")

    def create_button(self, text, command, font, color):
        button = tk.Button(self.main_frame, text=text, command=command, font=font, bg=color, fg="white", relief="flat", width=20, height=2)
        button.pack(pady=10)
        button.bind("<Enter>", lambda event, btn=button: self.on_hover(btn, "lightgray"))
        button.bind("<Leave>", lambda event, btn=button: self.on_leave(btn, color))

    def on_hover(self, button, color):
        button.config(bg=color)

    def on_leave(self, button, color):
        button.config(bg=color)

    def view_reservations(self):
        self.popup_window("Reservations", "SELECT * FROM reservation")

    def manage_room_status(self):
        window = tk.Toplevel(self.master)
        window.title("Manage Room Status")
        window.geometry("400x300")

        tk.Label(window, text="Room Number", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        room_number = tk.Entry(window, font=("Helvetica", 12))
        room_number.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(window, text="Status", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10)
        status = ttk.Combobox(window, values=["Available", "Occupied", "Out of Service"], font=("Helvetica", 12))
        status.grid(row=1, column=1, padx=10, pady=10)

        def update_status():
            db = connect_db()
            if db is None:
                return
            cursor = db.cursor()
            cursor.execute("UPDATE room SET roomStatus = %s WHERE roomNumber = %s", (status.get(), room_number.get()))
            db.commit()
            db.close()
            messagebox.showinfo("Success", "Room status updated.")

        tk.Button(window, text="Update", command=update_status, font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat").grid(row=2, column=0, columnspan=2, pady=10)

    def view_housekeeping_tasks(self):
        self.popup_window("Housekeeping Tasks", "SELECT * FROM housekeepingmaintenance")

    def billing_approval(self):
        window = tk.Toplevel(self.master)
        window.title("Billing Approval")
        window.geometry("500x300")

        db = connect_db()
        if db is None:
            return
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM billing WHERE PaymentStatus = 'Pending'")
        bills = cursor.fetchall()

        for bill in bills:
            frame = tk.LabelFrame(window, text=f"Bill ID: {bill['billId']}", font=("Helvetica", 12), padx=10, pady=10)
            frame.pack(fill="both", expand="yes", padx=10, pady=5)

            for key, value in bill.items():
                tk.Label(frame, text=f"{key}: {value}", font=("Helvetica", 10)).pack()

            def approve(b=bill['billId']):
                self.approve_payment(b)
                window.destroy()

            tk.Button(frame, text="Approve", command=approve, font=("Helvetica", 12), bg="#FF5722", fg="white", relief="flat").pack(pady=10)

        db.close()

    def manage_inventory(self):
        window = tk.Toplevel(self.master)
        window.title("Inventory Management")
        window.geometry("500x300")

        db = connect_db()
        if db is None:
            return
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventorysupplies")
        inventory = cursor.fetchall()

        for item in inventory:
            frame = tk.LabelFrame(window, text=item['ItemName'], font=("Helvetica", 12), padx=10, pady=10)
            frame.pack(fill="both", expand="yes", padx=10, pady=5)

            for key, value in item.items():
                tk.Label(frame, text=f"{key}: {value}", font=("Helvetica", 10)).pack()

            if item['QuantityInStock'] < item['ReorderLevel']:
                tk.Label(frame, text="⚠️ Needs restocking", fg="red", font=("Helvetica", 10)).pack()

                def restock(item_id=item['ItemID']):
                    self.restock_item(item_id)
                    window.destroy()

                tk.Button(frame, text="Restock +10", command=restock, font=("Helvetica", 12), bg="#8BC34A", fg="white", relief="flat").pack(pady=10)

        db.close()

    def view_restaurant_orders(self):
        self.popup_window("Restaurant Orders", "SELECT * FROM restaurantorders")

    def popup_window(self, title, query):
        window = tk.Toplevel(self.master)
        window.title(title)
        window.geometry("600x400")

        db = connect_db()
        if db is None:
            return
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            tk.Label(window, text=str(row), font=("Helvetica", 10)).pack(pady=5)

        db.close()

    def approve_payment(self, billing_id):
        db = connect_db()
        if db is None:
            return

        cursor = db.cursor()
        query = """
        UPDATE billing
        SET PaymentStatus = 'Paid'
        WHERE billId = %s
        """
        cursor.execute(query, (billing_id,))
        db.commit()
        db.close()

        messagebox.showinfo("Success", f"Payment for Bill {billing_id} approved.")

    def restock_item(self, item_id):
        db = connect_db()
        if db is None:
            return

        cursor = db.cursor()
        cursor.execute("UPDATE inventorysupplies SET QuantityInStock = QuantityInStock + 10 WHERE ItemID = %s", (item_id,))
        db.commit()
        db.close()

        messagebox.showinfo("Success", f"Item {item_id} restocked.")