from confluent_kafka import Producer, Consumer, KafkaError
import json
from pymongo import MongoClient
from datetime import datetime

def get_mongo_client():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['kafka_db']
    collection = db['messages']
    return collection

def get_producer_config():
    return {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'python-producer',
        'acks': 1,
        'retries': 5,
        'batch.size': 16384,
        'linger.ms': 5,
        'compression.type': 'gzip'
    }

def get_consumer_config(group_id):
    return {
        'bootstrap.servers': 'localhost:9092',
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }

def create_producer():
    return Producer(get_producer_config())

def create_consumer(topic):
    consumer = Consumer(get_consumer_config(f"{topic}-group"))
    consumer.subscribe([topic])
    return consumer

def send_message(producer, topic, message):
    try:
        producer.produce(topic=topic, value=json.dumps(message).encode('utf-8'))
        producer.flush()
        print(f"Message sent to {topic}: {message}")
    except KafkaError as e:
        print(f"Failed to send message: {e}")

def consume_messages(consumer, collection):
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Reached end of partition: {msg.partition()}")
            else:
                print(f"Error: {msg.error()}")
        else:
            message = json.loads(msg.value().decode('utf-8'))
            processed_message = {
                'original_message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'category': 'info' if message.get('key') == 'value' else 'warning'
            }
            try:
                collection.insert_one(processed_message)
                print(f"Saved to MongoDB: {processed_message}")
                consumer.commit(message=msg)
                print(f"Committed offset for message in partition {msg.partition()}")
            except Exception as e:
                print(f"Failed to save to MongoDB: {e}")

if __name__ == "__main__":
    topic = "test-topic"
    mongo_collection = get_mongo_client()
    producer = create_producer()
    send_message(producer, topic, {"key": "value"})
    send_message(producer, topic, {"key": "error"})
    consumer = create_consumer(topic)
    consume_messages(consumer, mongo_collection)