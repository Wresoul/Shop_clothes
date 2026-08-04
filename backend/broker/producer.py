import json
import logging
import threading  # Добавил для lock
from confluent_kafka import Producer  # Или from kafka import KafkaProducer — подгони под твою либу
from django.conf import settings

logger = logging.getLogger('broker.producer')

_producer_instance = None
_lock = threading.Lock()

def get_kafka_producer():
    global _producer_instance
    if _producer_instance is None:
        with _lock:
            if _producer_instance is None:
                conf = {
                    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
                    'broker.address.family': 'v4',  # Force IPv4
                }
                _producer_instance = Producer(conf)
                logger.info("Kafka producer initialized")  # Отфильтруется
    return _producer_instance

def send_to_kafka(topic, message):
    producer = get_kafka_producer()
    try:
        value = json.dumps(message).encode('utf-8') if isinstance(message, dict) else message
        producer.produce(topic, value=value)
        producer.poll(0)
        logger.debug(f"Sent message to Kafka topic {topic}: {message}")
    except Exception as e:
        logger.error(f"Kafka send error: {e}")