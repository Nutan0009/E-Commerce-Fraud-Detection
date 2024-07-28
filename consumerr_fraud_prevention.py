import tkinter as tk
from tkinter import ttk
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from kafka import KafkaConsumer
from twilio.rest import Client
import json
import threading

# Twilio credentials
TWILIO_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

# Load the trained model and scaler
model = joblib.load('decision_tree_model.pkl')
scaler = joblib.load('scaler.pkl')

# Create a Kafka consumer to receive transaction data
consumer = KafkaConsumer('fraud', bootstrap_servers='localhost:9092',
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

# Define all possible features
FEATURE_NAMES = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 
                  'oldbalanceDest', 'newbalanceDest', 'isFlaggedFraud', 
                  'type_CASH_OUT', 'type_DEBIT', 'type_PAYMENT', 
                  'type_TRANSFER', 'errorBalanceOrig', 'errorBalanceDest']

def predict_fraud(transaction):
    print(f"Predicting for transaction: {transaction}")  # Debugging

    # Initialize feature dictionary
    features = dict.fromkeys(FEATURE_NAMES, 0)
    features.update(transaction)
    
    # Create DataFrame for numerical features
    numerical_features = pd.DataFrame([{
        'amount': features['amount'],
        'oldbalanceOrg': features['oldbalanceOrg'],
        'newbalanceOrig': features['newbalanceOrig'],
        'oldbalanceDest': features['oldbalanceDest'],
        'newbalanceDest': features['newbalanceDest'],
        'errorBalanceOrig': features['errorBalanceOrig'],
        'errorBalanceDest': features['errorBalanceDest']
    }])
    
    print("Numerical features:", numerical_features)

    try:
        # Scaling the numerical features
        numerical_features_scaled = scaler.transform(numerical_features)
    except Exception as e:
        print(f"Error during scaling: {e}")
        return

    # Create DataFrame for all features
    scaled_features = pd.DataFrame(numerical_features_scaled, columns=[
        'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest',
        'newbalanceDest', 'errorBalanceOrig', 'errorBalanceDest'
    ])
    for feature in ['step', 'isFlaggedFraud', 'type_CASH_OUT', 'type_DEBIT', 
                    'type_PAYMENT', 'type_TRANSFER']:
        scaled_features[feature] = features[feature]
    
    # Ensure the column order matches the training phase
    final_features = scaled_features[FEATURE_NAMES]
    
    print(f"Final input features: {final_features}")

    try:
        # Predict using the loaded model
        prediction = model.predict(final_features)
        result = "Fraudulent" if prediction[0] == 1 else "Not Fraudulent"
        print(f"Prediction: {result}")  # Debugging

        # Update GUI with result
        update_gui_result(result)

        # Send alerts if fraud is detected
        if prediction[0] == 1:
            send_sms_alert(transaction.get('receiver_phone', ''))
            send_user_alert(transaction.get('email', ''))
    except Exception as e:
        print(f"Error during prediction: {e}")

def send_sms_alert(receiver_phone):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body="Fraudulent activity detected!",
            from_=TWILIO_PHONE_NUMBER,
            to=receiver_phone
        )
        print("SMS sent successfully!")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def send_user_alert(email):
    # Implement email sending functionality here if needed
    print(f"Alert sent to email: {email}")

def process_messages():
    for message in consumer:
        transaction = message.value
        print(f"Received transaction: {transaction}")
        predict_fraud(transaction)

def start_kafka_thread():
    thread = threading.Thread(target=process_messages)
    thread.daemon = True
    thread.start()

# Create the main window
root = tk.Tk()
root.title("Fraud Detection System")

# Set window size and center it
window_width = 600
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height/2 - window_height/2)
position_right = int(screen_width/2 - window_width/2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Styling
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12, "bold"))
style.configure("TButton", font=("Helvetica", 12, "bold"))

# Frame for results
result_frame = ttk.Frame(root, padding="20")
result_frame.pack(pady=20, fill="x")

# Result label
result_label = ttk.Label(result_frame, text="Awaiting transactions...", foreground="blue", anchor="center")
result_label.pack(pady=10, fill="x")

def update_gui_result(result):
    result_label.config(text=f"Prediction Result: {result}", foreground="red" if result == "Fraudulent" else "green")

# Start Kafka thread to process messages
start_kafka_thread()

root.mainloop()
