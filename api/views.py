from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from main.models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from main.models import Chat, Message
from .serializers import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from bot.llm import responder as bot_responder


class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            raise PermissionDenied("Este chat no te pertenece.")

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            contenido = serializer.validated_data['content']

            # Guardar mensaje enviado
            mensaje_usuario = Message.objects.create(
                chat=chat,
                content=contenido,
                message_type='user'
            )

            # Construir historial [(usuario, bot)]
            mensajes = list(chat.mensajes.order_by('index'))
            history = []
            for i in range(0, len(mensajes) - 1, 2):
                if mensajes[i].message_type == 'user' and mensajes[i+1].message_type == 'bot':
                    history.append((mensajes[i].content, mensajes[i+1].content))

            # Obtener respuesta del bot
            respuesta = bot_responder(contenido, history)

            # Guardar respuesta
            mensaje_bot = Message.objects.create(
                chat=chat,
                content=respuesta,
                message_type='bot'
            )

            return Response({
                'pregunta': mensaje_usuario.content,
                'respuesta': mensaje_bot.content
            }, status=201)

        return Response(serializer.errors, status=400)

class MessageListView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        try:
            chat = Chat.objects.get(id=chat_id, user=self.request.user)
        except Chat.DoesNotExist:
            raise PermissionDenied("Este chat no existe o no te pertenece.")
        return Message.objects.filter(chat=chat)
    
class LastMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            raise PermissionDenied("Este chat no existe o no te pertenece.")

        ultimo = chat.mensajes.order_by('-index').first()
        if not ultimo:
            return Response({'detail': 'Este chat no tiene mensajes.'}, status=204)
        
        return Response(MessageSerializer(ultimo).data)