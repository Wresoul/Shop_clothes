# message-processor/broker_config.py
import json
import os
from confluent_kafka import Producer, Consumer, KafkaError
from .mongo_utils import get_mongo_collection
from dotenv import load_dotenv
from datetime import datetime


load_dotenv('/Users/daniilradin/PycharmProjects/DjangoProject2/.env')

def get_producer_config():
    return {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
        'client.id': 'python-producer',
        'acks': 1,
        'retries': 5,
        'batch.size': 16384,
        'linger.ms': 5,
        'compression.type': 'gzip'
    }

def get_consumer_config(group_id):
    return {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
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
    topic = os.getenv('KAFKA_TOPIC')
    mongo_collection = get_mongo_collection()
    producer = create_producer()
    send_message(producer, topic, {"key": "value"})
    send_message(producer, topic, {"key": "error"})
    consumer = create_consumer(topic)
    consume_messages(consumer, mongo_collection)