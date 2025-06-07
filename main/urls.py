from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='chats/', permanent=True)),
    path('chats/', views.lista_chats, name='lista_chats'),
    path('chats/<int:chat_id>/', views.ver_chat, name='ver_chat'),
    path('chat/rename/<int:chat_id>/', views.rename_chat, name='rename_chat'),
    path('chat/delete/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('account/', views.account, name='account'),
]
