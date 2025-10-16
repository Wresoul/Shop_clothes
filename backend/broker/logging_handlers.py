import logging
import json
from django.conf import settings
from .producer import send_to_kafka
from datetime import datetime

class KafkaLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            log_message = {
                'level': record.levelname,
                'message': record.getMessage(),
                'logger_name': record.name,
                'timestamp': self.format_time(record),
                'file': record.pathname,
                'line': record.lineno,
                'extra': getattr(record, 'extra', {}),
            }
            # Отправляем как JSON str (подгони под producer.send: если нужно bytes — добавь .encode('utf-8'))
            topic = settings.KAFKA_TOPICS['logs']
            send_to_kafka(topic, log_message)
        except Exception as e:
            self.handleError(record)  # Fallback в console или stderr

    def format_time(self, record):
        return datetime.utcfromtimestamp(record.created).isoformat()

class NoKafkaFilter(logging.Filter):
    def filter(self, record):
        # Расширенный фильтр: Блокируй по модулю или ключевым словам
        if (
            'broker.producer' in record.name or
            'Sent message to Kafka' in record.msg or
            'KafkaLoggingHandler' in record.name or
            'emit' in record.msg  # Если emit логируется
        ):
            return False  # Не шлём в Kafka
        return True