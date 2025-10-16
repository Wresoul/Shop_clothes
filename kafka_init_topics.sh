#!/bin/sh
# Ждём брокер
until kafka-topics --bootstrap-server kafka:9092 --list > /dev/null 2>&1; do
  echo "Ждём Kafka..."
  sleep 5
done

# Создаём топики
kafka-topics --create --topic logs-topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --if-not-exists && echo "logs-topic создан"
kafka-topics --create --topic orders-topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --if-not-exists && echo "orders-topic создан"
kafka-topics --create --topic carts-topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --if-not-exists && echo "carts-topic создан"
kafka-topics --create --topic auth-topic --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --if-not-exists && echo "auth-topic создан"

echo "Топики готовы!"