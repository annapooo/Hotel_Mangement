#database name hotelManagement
#"C:\ProgramData\MySQL\MySQL Server 9.2\Data\hotelmanagement" db
import tkinter as tk
from tkinter import messagebox 
import mysql.connector
import os

from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    # Code for connecting to the database and performing queries
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("mysql_pass"),
        database="hotelManagement"                                             
    )

    return connection

def check_password(stored_hash, password):
    return(stored_hash==password)
# Employee Login Function
def employee_login(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employee WHERE Username = %s", (username,))
    user = cursor.fetchone()
    connection.close()

    if user and check_password(user[5], password):  
        return True, user
    return False, None

# Guest Login Function
def guest_login(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM guests WHERE Username = %s", (username,))
    user = cursor.fetchone()
    connection.close()

    if user and check_password(user[5], password):  
        return True, user
    return False, None

def show_employee_dashboard(root, username):
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Display employee dashboard
    welcome_label = tk.Label(root, text=f"Welcome, {username}!", font=('times', 16))
    welcome_label.pack(pady=20)

    logout_button = tk.Button(root, text="Logout", command=lambda: logout(root))
    logout_button.pack(pady=10)

# Function to show Guest Dashboard
def show_guest_dashboard(root, username):
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Display guest dashboard
    welcome_label = tk.Label(root, text=f"Welcome, {username}!", font=('times', 16))
    welcome_label.pack(pady=20)

    logout_button = tk.Button(root, text="Logout", command=lambda: logout(root))
    logout_button.pack(pady=10)

# Logout function to return to the login screen
def logout(root):
    for widget in root.winfo_children():
        widget.destroy()

    create_entry_screen(root)

def create_login_screen(root, user_type):
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    bg = tk.PhotoImage(file = "./assets/loginbg.png") 
    label1 =tk.Label( root, image = bg) 
    label1.place(x = 0, y = 0) 

    login_label = tk.Label(root, text="Login",bg="#fff1f3",font=('courier new', 20))
    login_label.pack(pady=20)

    username_label = tk.Label(root, text="Username:",bg="#fff1f3",font=('times',12))
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:",bg="#fff1f3",font=('times',12))
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    
    if user_type.lower()=="guest":
        register_button=tk.Button(root,text="register",command=lambda: create_guest_registration_screen(root))
        register_button.pack(pady=30)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        if user_type == "Employee":
            success, user_data = employee_login(username, password)
        else:
            success, user_data = guest_login(username, password)

        if success:
            if user_type == "Employee":
                show_employee_dashboard(root, user_data[1])
            elif user_type == "Guest":
                show_guest_dashboard(root, user_data[1])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_button = tk.Button(root, text="Login", command=handle_login)
    login_button.pack(pady=20)

    root.mainloop()

def register_guest(username, password, name, email, phone):
    connection = get_db_connection()
    cursor = connection.cursor()
    hashed_password = password 
    cursor.execute("INSERT INTO guests (Username, Password, Name, Email, Phone) VALUES (%s, %s, %s, %s, %s)",
                   (username, hashed_password, name, email, phone))
    connection.commit()
    connection.close()
    messagebox.showinfo("Registration Success", "Guest Registered Successfully!")

def create_guest_registration_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

    register_label = tk.Label(root, text="Guest Registration", font=('courier new', 20))
    register_label.pack(pady=20)

    # Username and Password
    username_label = tk.Label(root, text="Username:", font=('times', 12))
    username_label.pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:", font=('times', 12))
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    # Other guest details
    name_label = tk.Label(root, text="Name:", font=('times', 12))
    name_label.pack(pady=5)
    name_entry = tk.Entry(root)
    name_entry.pack(pady=5)

    email_label = tk.Label(root, text="Email:", font=('times', 12))
    email_label.pack(pady=5)
    email_entry = tk.Entry(root)
    email_entry.pack(pady=5)

    phone_label = tk.Label(root, text="Phone:", font=('times', 12))
    phone_label.pack(pady=5)
    phone_entry = tk.Entry(root)
    phone_entry.pack(pady=5)

    def handle_registration():
        username = username_entry.get()
        password = password_entry.get()
        name = name_entry.get()
        email = email_entry.get()
        phone = phone_entry.get()

        if not username or not password or not name or not email or not phone:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        register_guest(username, password, name, email, phone)

    register_button = tk.Button(root, text="Register", command=handle_registration)
    register_button.pack(pady=20)

    root.mainloop() 

# Function to create the entry page for selecting Guest or Employee
def create_entry_screen(root):
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.destroy()
    bg = tk.PhotoImage(file = "./assets/startbg.png") 
    label1 =tk.Label( root, image = bg) 
    label1.place(x = 0, y = 0) 

    entry_label = tk.Label(root, text="Select User Type", font=('Helvetica', 20))
    entry_label.pack(pady=20)

    employee_button = tk.Button(root, text="Login as Employee", command=lambda: create_login_screen(root, "Employee"))
    employee_button.pack(pady=10)

    guest_button = tk.Button(root, text="Login as Guest", command=lambda: create_login_screen(root, "Guest"))
    guest_button.pack(pady=10)

    root.mainloop()

# Main function to start the application
def main():
    root = tk.Tk()
    root.title("Hotel Management System")
    root.geometry("448x400")

    create_entry_screen(root)

if __name__ == "__main__":
    main()




