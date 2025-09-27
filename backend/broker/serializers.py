# message-processor/serializers.py
from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', read_only=True)  # MongoDB _id
    original_message = serializers.DictField()  # Поле для словаря
    timestamp = serializers.CharField()
    category = serializers.CharField()

    def create(self, validated_data):
        collection = self.context['mongo_collection']
        result = collection.insert_one(validated_data)
        validated_data['_id'] = str(result.inserted_id)
        return validated_data

    def update(self, instance, validated_data):
        collection = self.context['mongo_collection']
        collection.update_one({'_id': instance['_id']}, {'$set': validated_data})
        return validated_data