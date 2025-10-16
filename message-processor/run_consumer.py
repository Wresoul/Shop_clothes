from broker_config import create_consumer, get_mongo_collection
from datetime import datetime
import json

def process_message(msg_value):
    # Парсим и обогащаем
    original = json.loads(msg_value)
    return {
        'original': original,
        'processed_at': datetime.utcnow().isoformat(),
        'source_topic': 'unknown'  # Добавим в consume
    }

def consume_loop(topics):
    collection = get_mongo_collection()
    consumer = create_consumer('multi-group')  # Один consumer на все
    consumer.subscribe(topics)

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        try:
            value = msg.value().decode('utf-8')
            processed = process_message(value)
            processed['source_topic'] = msg.topic()
            collection.insert_one(processed)
            print(f"Saved to Mongo from {msg.topic()}: {processed}")
            consumer.commit(msg)
        except Exception as e:
            print(f"Process error: {e}")

if __name__ == "__main__":
    topics = ['logs-topic', 'orders-topic', 'carts-topic']
    consume_loop(topics)