from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.lista_chats, name='lista_chats'),
    path('chats/<int:chat_id>/', views.ver_chat, name='ver_chat'),
]
