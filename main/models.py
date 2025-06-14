from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    class State(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        INACTIVE = 'inactive', 'Inactivo'
        ARCHIVED = 'archived', 'Archivado'


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    chat_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    state = models.CharField(
        max_length=10,
        choices=State.choices,
        default=State.ACTIVE
    )
    
    def __str__(self):
        return f"Chat '{self.chat_name}' de {self.user.username}"

class Message(models.Model):
    class MessageType(models.TextChoices):
        USER = 'user', 'Usuario'
        BOT = 'bot', 'Bot'
        CODE = 'code', 'Código'
        SYSTEM = 'system', 'Sistema'

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='mensajes')
    index = models.PositiveIntegerField(editable=False)  # Para mantener orden explícito
    message_type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.USER
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['index']  # Para mantener el orden de los mensajes 

    def save(self, *args, **kwargs):
        if self.pk is None:
            last_msg = Message.objects.filter(chat=self.chat).order_by('-index').first()
            self.index = 0 if not last_msg else last_msg.index + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.message_type} → {self.content[:40]}"
