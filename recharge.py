import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
import random
import string

# Connect to SQLite database
conn = sqlite3.connect('recharge.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    value INTEGER,
                    expiry_date TEXT,
                    available INTEGER DEFAULT 1,
                    ticket_number TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    phone_number TEXT,
                    balance INTEGER)''')


# Function to generate tickets
def generate_tickets():
    values = [1, 2, 5, 10]
    expiry_date = datetime.now() + timedelta(days=10)
    for _ in range(100):
        value = random.choice(values)
        ticket_id = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        ticket_number = ''.join(random.choices(
            string.digits, k=10))  # Generate ticket number
        cursor.execute("INSERT INTO tickets (id, value, expiry_date, ticket_number) VALUES (?, ?, ?, ?)",
                       (ticket_id, value, expiry_date, ticket_number))
    conn.commit()


# Function to generate users
def generate_users(num_users):
    for _ in range(num_users):
        # Generate random phone number
        phone_number = ''.join(random.choices(string.digits, k=10))
        balance = random.randint(0, 100)  # Generate random balance
        cursor.execute("INSERT INTO users (phone_number, balance) VALUES (?, ?)",
                       (phone_number, balance))
    conn.commit()


# Function to add recharge
def add_recharge(phone_number, ticket_number):
    cursor.execute(
        "SELECT value, available FROM tickets WHERE ticket_number=?", (ticket_number,))
    ticket = cursor.fetchone()
    if ticket:
        value, available = ticket
        if available:
            cursor.execute(
                "SELECT balance FROM users WHERE phone_number=?", (phone_number,))
            current_balance = cursor.fetchone()
            if current_balance:
                current_balance = current_balance[0]
                new_balance = current_balance + value
                cursor.execute(
                    "UPDATE users SET balance=? WHERE phone_number=?", (new_balance, phone_number))
                cursor.execute(
                    "UPDATE tickets SET available=0 WHERE ticket_number=?", (ticket_number,))
                conn.commit()
                messagebox.showinfo(
                    "Success", f"Recharge of ${value} added successfully to {phone_number}. New balance: ${new_balance}")
            else:
                messagebox.showerror("Error", "User not found.")
        else:
            messagebox.showerror("Error", "Ticket has already been used.")
    else:
        messagebox.showerror("Error", "Invalid ticket number.")


# Function to handle button click
def recharge_button_click():
    ticket_number = ticket_entry.get()
    phone_number = phone_entry.get()
    add_recharge(phone_number, ticket_number)


# Function to handle number button clicks
def number_button_click(number):
    if active_entry == 'ticket':
        current_text = ticket_entry.get()
        ticket_entry.delete(0, tk.END)
        ticket_entry.insert(tk.END, current_text + str(number))
    elif active_entry == 'phone':
        current_text = phone_entry.get()
        phone_entry.delete(0, tk.END)
        phone_entry.insert(tk.END, current_text + str(number))


# Function to handle focus in event for ticket entry
def on_ticket_focus_in(event):
    global active_entry
    active_entry = 'ticket'


# Function to handle focus in event for phone entry
def on_phone_focus_in(event):
    global active_entry
    active_entry = 'phone'


# GUI
root = tk.Tk()
root.title("Recharge Telephone Application")
root.geometry("350x700")  # Adjusted size to resemble iPhone dimensions

# Frame for phone display
phone_frame = tk.Frame(root, bg='#34495e', bd=5)
phone_frame.place(relx=0.5, rely=0.05, relwidth=0.9, relheight=0.9, anchor='n')

# Labels
tk.Label(phone_frame, text="Enter the ticket number:",
         bg='#34495e', fg='white', font=('Arial', 16)).pack()
ticket_entry = tk.Entry(phone_frame, font=('Arial', 16))
ticket_entry.pack()
ticket_entry.bind('<FocusIn>', on_ticket_focus_in)

tk.Label(phone_frame, text="Enter your phone number:",
         bg='#34495e', fg='white', font=('Arial', 16)).pack()
phone_entry = tk.Entry(phone_frame, font=('Arial', 16))
phone_entry.pack()
phone_entry.bind('<FocusIn>', on_phone_focus_in)

# Number buttons
number_buttons_frame = tk.Frame(phone_frame, bg='#34495e')
number_buttons_frame.place(
    relx=0.5, rely=0.3, relwidth=0.9, relheight=0.6, anchor='n')

numbers = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

button_font = ('Arial', 20)  # Adjust font size

for i in range(4):
    for j in range(3):
        tk.Button(number_buttons_frame, text=numbers[i][j], font=button_font, width=3, height=2,
                  command=lambda num=numbers[i][j]: number_button_click(num), bg='#2c3e50', fg='white').grid(row=i, column=j, sticky='nsew', padx=5, pady=5)

# Button
recharge_button = tk.Button(phone_frame, text="Recharge", font=('Arial', 16),
                            command=recharge_button_click, bg='#2ecc71', fg='white')
recharge_button.place(relx=0.5, rely=0.95, anchor='n')

# Generate tickets and users
generate_tickets()
generate_users(100)  # Generate 100 users

# Set initial active entry
active_entry = 'ticket'

root.mainloop()
