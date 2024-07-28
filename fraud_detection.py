import tkinter as tk
from tkinter import messagebox
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from twilio.rest import Client
import requests
from requests.auth import HTTPBasicAuth

# Define Twilio credentials


# Load the pre-trained model and scaler from saved files
model = joblib.load('decision_tree_model.pkl')
scaler = joblib.load('scaler.pkl')

def send_sms_alert(receiver_phone):
    """Function to send an SMS alert using Twilio API."""
    try:
        response = requests.post(
            f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json',
            auth=HTTPBasicAuth(TWILIO_SID, TWILIO_AUTH_TOKEN),
            data={
                'Body': 'Fraudulent activity detected!',
                'From': TWILIO_PHONE_NUMBER,
                'To': receiver_phone
            },
            verify=False  # Disable SSL certificate verification
        )
        
        # Log the response status for debugging
        print(response.status_code)
        print(response.text)
        
        if response.status_code == 201:
            print("SMS sent successfully!")
        else:
            print(f"Failed to send SMS. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def save_login_details():
    """Function to save user login details and display the fraud detection form."""
    username = username_entry.get()
    password = password_entry.get()
    receiver_phone = phone_entry.get()
    
    # Save login details to a CSV file
    login_details = pd.DataFrame([[username, password, receiver_phone]], columns=["Username", "Password", "ReceiverPhone"])
    login_details.to_csv("login_details.csv", mode='a', header=False, index=False)
    
    # Switch frames from login to form
    login_frame.pack_forget()
    form_frame.pack(pady=20)

def predict_fraud():
    """Function to predict fraud and update the UI with the result."""
    # Collect and normalize input data
    step = 1  # Example value, adjust as needed
    amount = float(amount_entry.get())
    old_balance_orig = float(old_balance_orig_entry.get())
    new_balance_orig = float(new_balance_orig_entry.get())
    old_balance_dest = float(old_balance_dest_entry.get())
    new_balance_dest = float(new_balance_dest_entry.get())
    is_flagged_fraud = int(is_flagged_fraud_var.get())
    
    # Set transaction type based on user selection
    type_cash_out = 1 if type_var.get() == 'cash_out' else 0
    type_debit = 1 if type_var.get() == 'debit' else 0
    type_payment = 1 if type_var.get() == 'payment' else 0
    type_transfer = 1 if type_var.get() == 'transfer' else 0

    # Compute error balances
    error_balance_orig = new_balance_orig - old_balance_orig
    error_balance_dest = new_balance_dest - old_balance_dest

    # Prepare data for prediction
    input_data = pd.DataFrame([[amount, old_balance_orig, new_balance_orig, old_balance_dest, new_balance_dest, error_balance_orig, error_balance_dest]],
                              columns=['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'errorBalanceOrig', 'errorBalanceDest'])
    input_data_scaled = scaler.transform(input_data)

    # Combine scaled and non-scaled features
    input_data_scaled = pd.DataFrame(input_data_scaled, columns=['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'errorBalanceOrig', 'errorBalanceDest'])
    input_data_scaled['step'] = step
    input_data_scaled['isFlaggedFraud'] = is_flagged_fraud
    input_data_scaled['type_CASH_OUT'] = type_cash_out
    input_data_scaled['type_DEBIT'] = type_debit
    input_data_scaled['type_PAYMENT'] = type_payment
    input_data_scaled['type_TRANSFER'] = type_transfer

    # Ensure the correct order of features
    input_data_scaled = input_data_scaled[['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'isFlaggedFraud',
                                           'type_CASH_OUT', 'type_DEBIT', 'type_PAYMENT', 'type_TRANSFER', 'errorBalanceOrig', 'errorBalanceDest']]

    # Make a prediction
    prediction = model.predict(input_data_scaled)
    
    # Update UI with the prediction result
    result_text = "Fraud detected!" if prediction[0] == 1 else "No fraud detected."
    receiver_phone = phone_entry.get()
    send_sms_alert(receiver_phone)
    
    result_label.config(text=result_text)

def center_window(window, width, height):
    """Function to center the window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

# Create and configure the main application window
root = tk.Tk()
root.title("Fraud Detection System")

# Set the window size and position it at the center
window_width = 800
window_height = 600
center_window(root, window_width, window_height)

# Define fonts and colors
title_font = ("Helvetica", 16, "bold")
label_font = ("Helvetica", 12)
entry_font = ("Helvetica", 12)
button_font = ("Helvetica", 12, "bold")
button_bg_color = "#4CAF50"
button_fg_color = "#FFFFFF"

# Create the login frame
login_frame = tk.Frame(root)
login_frame.pack(pady=20)

title_label = tk.Label(login_frame, text="Login", font=title_font)
title_label.grid(row=0, columnspan=2, pady=10)

email_label = tk.Label(login_frame, text="Email:", font=label_font)
email_label.grid(row=1, column=0, padx=10, pady=5)
email_entry = tk.Entry(login_frame, font=entry_font)
email_entry.grid(row=1, column=1, padx=10, pady=5)

username_label = tk.Label(login_frame, text="Username:", font=label_font)
username_label.grid(row=2, column=0, padx=10, pady=5)
username_entry = tk.Entry(login_frame, font=entry_font)
username_entry.grid(row=2, column=1, padx=10, pady=5)

password_label = tk.Label(login_frame, text="Password:", font=label_font)
password_label.grid(row=3, column=0, padx=10, pady=5)
password_entry = tk.Entry(login_frame, show="*", font=entry_font)
password_entry.grid(row=3, column=1, padx=10, pady=5)

phone_label = tk.Label(login_frame, text="Phone Number:", font=label_font)
phone_label.grid(row=4, column=0, padx=10, pady=5)
phone_entry = tk.Entry(login_frame, font=entry_font)
phone_entry.grid(row=4, column=1, padx=10, pady=5)

login_button = tk.Button(login_frame, text="Login", font=button_font, bg=button_bg_color, fg=button_fg_color, command=save_login_details)
login_button.grid(row=5, columnspan=2, pady=10)

# Create the fraud detection form frame
form_frame = tk.Frame(root)
form_frame.pack_forget()

title_label_form = tk.Label(form_frame, text="Fraud Detection Form", font=title_font)
title_label_form.grid(row=0, columnspan=2, pady=10)

amount_label = tk.Label(form_frame, text="Amount:", font=label_font)
amount_label.grid(row=1, column=0, padx=10, pady=5)
amount_entry = tk.Entry(form_frame, font=entry_font)
amount_entry.grid(row=1, column=1, padx=10, pady=5)

old_balance_orig_label = tk.Label(form_frame, text="Old Balance Origin:", font=label_font)
old_balance_orig_label.grid(row=2, column=0, padx=10, pady=5)
old_balance_orig_entry = tk.Entry(form_frame, font=entry_font)
old_balance_orig_entry.grid(row=2, column=1, padx=10, pady=5)

new_balance_orig_label = tk.Label(form_frame, text="New Balance Origin:", font=label_font)
new_balance_orig_label.grid(row=3, column=0, padx=10, pady=5)
new_balance_orig_entry = tk.Entry(form_frame, font=entry_font)
new_balance_orig_entry.grid(row=3, column=1, padx=10, pady=5)

old_balance_dest_label = tk.Label(form_frame, text="Old Balance Destination:", font=label_font)
old_balance_dest_label.grid(row=4, column=0, padx=10, pady=5)
old_balance_dest_entry = tk.Entry(form_frame, font=entry_font)
old_balance_dest_entry.grid(row=4, column=1, padx=10, pady=5)

new_balance_dest_label = tk.Label(form_frame, text="New Balance Destination:", font=label_font)
new_balance_dest_label.grid(row=5, column=0, padx=10, pady=5)
new_balance_dest_entry = tk.Entry(form_frame, font=entry_font)
new_balance_dest_entry.grid(row=5, column=1, padx=10, pady=5)

is_flagged_fraud_var = tk.IntVar()
is_flagged_fraud_checkbutton = tk.Checkbutton(form_frame, text="Is Flagged Fraud", variable=is_flagged_fraud_var, font=label_font)
is_flagged_fraud_checkbutton.grid(row=6, columnspan=2, pady=5)

type_var = tk.StringVar()
type_label = tk.Label(form_frame, text="Transaction Type:", font=label_font)
type_label.grid(row=7, column=0, padx=10, pady=5)
type_options = ["cash_out", "debit", "payment", "transfer"]
type_menu = tk.OptionMenu(form_frame, type_var, *type_options)
type_menu.grid(row=7, column=1, padx=10, pady=5)

submit_button = tk.Button(form_frame, text="Submit", font=button_font, bg=button_bg_color, fg=button_fg_color, command=predict_fraud)
submit_button.grid(row=8, columnspan=2, pady=10)

result_label = tk.Label(form_frame, text="", font=title_font, fg="red")
result_label.grid(row=9, columnspan=2, pady=10)

# Run the application
root.mainloop()
