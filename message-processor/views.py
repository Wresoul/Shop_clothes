# message-processor/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from bson import ObjectId
from .mongo_utils import get_mongo_collection
from .serializers import MessageSerializer

class MessageViewSet(viewsets.ViewSet):
    def get_collection(self):
        return get_mongo_collection()

    def list(self, request):
        collection = self.get_collection()
        messages = list(collection.find())
        # Преобразуем ObjectId в строку
        for message in messages:
            message['_id'] = str(message['_id'])
        serializer = MessageSerializer(messages, many=True, context={'mongo_collection': collection})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        collection = self.get_collection()
        try:
            message = collection.find_one({'_id': ObjectId(pk)})
            if not message:
                return Response({'error': 'Message not found'}, status=404)
            message['_id'] = str(message['_id'])
            serializer = MessageSerializer(message, context={'mongo_collection': collection})
            return Response(serializer.data)
        except:
            return Response({'error': 'Invalid ID'}, status=400)

    def create(self, request):
        collection = self.get_collection()
        serializer = MessageSerializer(data=request.data, context={'mongo_collection': collection})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        collection = self.get_collection()
        try:
            message = collection.find_one({'_id': ObjectId(pk)})
            if not message:
                return Response({'error': 'Message not found'}, status=404)
            serializer = MessageSerializer(message, data=request.data, context={'mongo_collection': collection})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except:
            return Response({'error': 'Invalid ID'}, status=400)

    def destroy(self, request, pk=None):
        collection = self.get_collection()
        try:
            result = collection.delete_one({'_id': ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({'error': 'Message not found'}, status=404)
            return Response(status=204)
        except:
            return Response({'error': 'Invalid ID'}, status=400)