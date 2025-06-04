from django.urls import path
from .views import ChatListCreateView, MessageCreateView, MessageListView, LastMessageView

urlpatterns = [
    path('chats/', ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:chat_id>/mensajes/', MessageCreateView.as_view(), name='message-create'),
    path('chats/<int:chat_id>/historial/', MessageListView.as_view(), name='message-list'),
    path('chats/<int:chat_id>/ultimo/', LastMessageView.as_view(), name='ultimo-mensaje'),
]
