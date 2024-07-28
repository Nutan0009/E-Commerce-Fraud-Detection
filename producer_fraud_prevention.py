# # producer.py
# from kafka import KafkaProducer
# import json
# import time

# # Kafka producer setup
# producer = KafkaProducer(bootstrap_servers='localhost:9092',
#                          value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# def produce_transaction(transaction):
#     producer.send('fraud', transaction)
#     producer.flush()

# # Simulate sending transactions
# for _ in range(10):
#     transaction = {'step': 1, 'amount': 5000, 'oldbalanceOrg': 10000, 'newbalanceOrig': 5000,
#                    'oldbalanceDest': 0, 'newbalanceDest': 5000, 'isFlaggedFraud': 0,
#                    'type_CASH_OUT': 1, 'type_DEBIT': 0, 'type_PAYMENT': 0, 'type_TRANSFER': 0,
#                    'receiver_phone': '+1234567890', 'email': 'example@example.com'}
#     produce_transaction(transaction)
#     print(f"Sent transaction: {transaction}")
#     time.sleep(5)  # Adjust the delay for demonstration purposes

from kafka import KafkaProducer
import json
import time

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'fraud'

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def produce_transaction(transaction):
    try:
        producer.send(KAFKA_TOPIC, transaction)
        producer.flush()
        print(f"Sent transaction: {transaction}")
    except Exception as e:
        print(f"Failed to send transaction: {e}")

def generate_transaction():
    return {
        'step': 1,
        'amount': 5000,
        'oldbalanceOrg': 10000,
        'newbalanceOrig': 5000,
        'oldbalanceDest': 0,
        'newbalanceDest': 5000,
        'isFlaggedFraud': 0,
        'type_CASH_OUT': 1,
        'type_DEBIT': 0,
        'type_PAYMENT': 0,
        'type_TRANSFER': 0,
        'receiver_phone': '+1234567890',
        'email': 'example@example.com'
    }

# Simulate sending transactions
if __name__ == "__main__":
    while True:
        transaction = generate_transaction()
        produce_transaction(transaction)
        time.sleep(5)  # Adjust the delay for demonstration purposes

