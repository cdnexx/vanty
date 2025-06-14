import time
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Chat, Message, User
from django.core.exceptions import PermissionDenied
from bot.llm import responder as bot_responder
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

DEFAULT_AVATAR = 'X'

@login_required(login_url='/login/')
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
            # Obtener mensajes del chat
            mensajes = list(nuevo_chat.mensajes.order_by('index'))

            # Obtener respuesta del bot
            inicio = time.time()
            respuesta = bot_responder(mensajes)
            fin = time.time()
            tiempo_respuesta = fin - inicio # Tiempo en segundos

            # Crear respuesta del bot
            Message.objects.create(
                chat=nuevo_chat,
                content=respuesta,
                message_type='bot',
                response_time=tiempo_respuesta
            )

            return redirect('ver_chat', chat_id=nuevo_chat.id)

    chat_list = Chat.objects.filter(user=request.user).order_by('-updated_at')

    user = request.user.first_name or request.user.username
    avatar = user[0].upper() if user else DEFAULT_AVATAR
    chats = Chat.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'main/main.html', {'logged': True, 'chat_list': chat_list, 'avatar': avatar})

@login_required(login_url='/login/')
def ver_chat(request, chat_id):
    chat_list = Chat.objects.filter(user=request.user).order_by('-updated_at')
    chat = Chat.objects.get(id=chat_id)

    if chat.user != request.user:
        raise PermissionDenied

    user = request.user.first_name or request.user.username
    avatar = user[0].upper() if user else DEFAULT_AVATAR

    if request.method == "POST":
        contenido = request.POST.get("contenido", "").strip()
        if contenido:
            Message.objects.create(chat=chat, content=contenido, message_type='user')

            mensajes = list(chat.mensajes.order_by('index'))
            history = []
            for i in range(0, len(mensajes) - 1, 2):
                if mensajes[i].message_type == 'user' and mensajes[i+1].message_type == 'bot':
                    history.append((mensajes[i].content, mensajes[i+1].content))

            mensajes = list(chat.mensajes.order_by('index'))
            inicio = time.time()
            respuesta = bot_responder(mensajes)
            fin = time.time()
            tiempo_respuesta = fin - inicio # Tiempo en segundos
            Message.objects.create(chat=chat, content=respuesta, message_type='bot', response_time=tiempo_respuesta)

        # AJAX: retornar solo los mensajes como HTML parcial
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            mensajes = chat.mensajes.order_by('index')
            html = render_to_string('main/partials/chat_messages.html', {
                'mensajes': mensajes
            })
            return HttpResponse(html)

        # Normal POST → recargar la vista completa
        return redirect('ver_chat', chat_id=chat.id)

    mensajes = chat.mensajes.order_by('index')
    return render(request, 'main/chat.html', {
        'logged': True,
        'chat_list': chat_list,
        'current_chat_id': chat_id,
        'chat': chat,
        'mensajes': mensajes,
        'avatar': avatar
    })

@login_required(login_url='/login/')
def account(request):
    user = request.user
    chat_list = Chat.objects.filter(user=request.user)
    if request.method == "POST":
        new_first_name = request.POST.get("first_name", "").strip()
        new_last_name = request.POST.get("last_name", "").strip()
        new_email = request.POST.get("email", "").strip()

        if new_first_name:
            user.first_name = new_first_name
        if new_last_name:
            user.last_name = new_last_name
        if new_email:
            user.email = new_email

        user.save()
        return redirect('lista_chats')

    username = request.user.first_name or request.user.username
    avatar = username[0].upper() if username else DEFAULT_AVATAR
    return render(request, 'main/account.html', {'user': user, 'logged': True,'chat_list': chat_list, 'avatar': avatar})

def rename_chat(request, chat_id):
    if request.method == "POST":
        new_name = request.POST.get("new_name")
        
        # Obtener el chat
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Renombrar el chat
        chat.chat_name = new_name
        chat.save()
        
        return JsonResponse({"status": "success", "new_name": new_name})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def delete_chat(request, chat_id):
    if request.method == "POST":
        # Obtener el chat
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Eliminar el chat
        chat.delete()
        # chat.state = Chat.State.INACTIVE
        # chat.save()
        
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)