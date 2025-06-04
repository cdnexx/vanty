from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Chat, Message, User
from django.core.exceptions import PermissionDenied
from bot.llm import responder as bot_responder

@login_required
def lista_chats(request):
    if request.method == "POST":
        contenido = request.POST.get("contenido", "").strip()
        if contenido:
            # Crear nuevo chat
            nuevo_chat = Chat.objects.create(
                user=request.user,
                chat_name=f"{contenido[:20]}...",
            )

            # Crear mensaje del usuario
            Message.objects.create(
                chat=nuevo_chat,
                content=contenido,
                message_type='user'
            )

            # Obtener respuesta del bot
            respuesta = bot_responder(contenido, [])

            # Crear respuesta del bot
            Message.objects.create(
                chat=nuevo_chat,
                content=respuesta,
                message_type='bot'
            )

            return redirect('ver_chat', chat_id=nuevo_chat.id)

    chat_list = Chat.objects.filter(user=request.user)
    user = request.user.first_name or request.user.username
    avatar = user[0].upper() if user else 'U'
    chats = Chat.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'main/main.html', {'chat_list': chat_list, 'avatar': avatar})

@login_required
def ver_chat(request, chat_id):
    chat_list = Chat.objects.filter(user=request.user)
    chat = Chat.objects.get(id=chat_id)
    if chat.user != request.user:
        raise PermissionDenied
    
    user = request.user.first_name or request.user.username
    avatar = user[0].upper() if user else 'U'

    if request.method == "POST":
        contenido = request.POST.get("contenido", "").strip()
        if contenido:
            # 1. Guardar mensaje del usuario
            Message.objects.create(chat=chat, content=contenido, message_type='user')

            # 2. Construir historial [(usuario, bot), ...]
            mensajes = list(chat.mensajes.order_by('index'))
            history = []
            for i in range(0, len(mensajes) - 1, 2):
                if mensajes[i].message_type == 'user' and mensajes[i+1].message_type == 'bot':
                    history.append((mensajes[i].content, mensajes[i+1].content))

            # 3. Obtener respuesta del bot
            respuesta = bot_responder(contenido, history)

            # 4. Guardar respuesta del bot
            Message.objects.create(chat=chat, content=respuesta, message_type='bot')

            return redirect('ver_chat', chat_id=chat.id)

    mensajes = chat.mensajes.order_by('index')
    return render(request, 'main/chat.html', {'chat_list': chat_list, 'chat': chat, 'mensajes': mensajes, 'avatar': avatar})