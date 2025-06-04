from rest_framework import serializers
from main.models import Chat, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ['index']  # Se asgina automáticamente
        read_only_fields = ['chat', 'sent_at', 'message_type']

class ChatSerializer(serializers.ModelSerializer):
    mensajes = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'chat_name', 'state', 'created_at', 'updated_at', 'mensajes']
        read_only_fields = ['created_at', 'updated_at']

