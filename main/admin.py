from django.contrib import admin
from .models import Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['chat_name', 'user', 'state', 'created_at']
    search_fields = ['chat_name', 'user__username']
    list_filter = ['state']
    ordering = ['-created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'index', 'message_type', 'content', 'sent_at']
    list_filter = ['message_type']
    search_fields = ['content']
    ordering = ['chat', 'index']
