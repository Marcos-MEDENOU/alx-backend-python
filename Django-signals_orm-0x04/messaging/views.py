from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from .models import Message, Notification
from .forms import DeleteAccountForm

User = get_user_model()

@login_required
@require_http_methods(["GET", "POST"])
def delete_user(request):
    """
    View to handle user account deletion with confirmation.
    The actual user deletion will be handled by the post_delete signal.
    """
    user = request.user
    
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST, user=user)
        if form.is_valid():
            try:
                # This will trigger the post_delete signal
                username = user.username
                user.delete()
                # Log the user out after deletion
                logout(request)
                messages.success(request, f'Account {username} has been successfully deleted.')
                return redirect('home')  # Replace 'home' with your actual home URL name
            except Exception as e:
                messages.error(request, f'An error occurred while deleting your account: {str(e)}')
                return redirect('profile')
    else:
        form = DeleteAccountForm()
    
    return render(request, 'messaging/delete_account_confirm.html', {'form': form})


@login_required
def inbox(request):
    """
    Affiche la boîte de réception de l'utilisateur avec les conversations.
    Utilise select_related pour optimiser les requêtes.
    """
    # Récupérer les messages reçus et envoyés
    received_messages = Message.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by('-timestamp')
    
    sent_messages = Message.objects.filter(
        sender=request.user
    ).select_related('receiver').order_by('-timestamp')
    
    # Créer une liste unique de conversations
    conversations = {}
    
    # Traiter les messages reçus
    for msg in received_messages:
        other_user = msg.sender
        if other_user not in conversations:
            conversations[other_user] = {
                'last_message': msg,
                'unread_count': Message.objects.filter(
                    sender=other_user,
                    receiver=request.user,
                    is_read=False
                ).count()
            }
    
    # Traiter les messages envoyés
    for msg in sent_messages:
        other_user = msg.receiver
        if other_user not in conversations:
            conversations[other_user] = {
                'last_message': msg,
                'unread_count': 0
            }
    
    # Trier les conversations par date du dernier message
    sorted_conversations = sorted(
        conversations.items(),
        key=lambda x: x[1]['last_message'].timestamp,
        reverse=True
    )
    
    return render(request, 'messaging/inbox.html', {
        'conversations': sorted_conversations,
    })


@login_required
def conversation(request, user_id):
    """
    Affiche la conversation avec un utilisateur spécifique.
    Utilise select_related et prefetch_related pour optimiser les requêtes.
    """
    other_user = get_object_or_404(get_user_model(), pk=user_id)
    
    # Marquer les messages comme lus
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Récupérer les messages avec optimisation des requêtes
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related('sender', 'receiver').order_by('timestamp')
    
    # Si c'est une requête AJAX, renvoyer uniquement les messages
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'messaging/_messages.html', {
            'messages': messages,
            'current_user': request.user
        })
    
    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages
    })


@login_required
@require_http_methods(["POST"])
def send_message(request, user_id):
    """
    Envoie un message à un utilisateur.
    """
    receiver = get_object_or_404(get_user_model(), pk=user_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, "Message cannot be empty.")
    else:
        # Créer le message
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        
        # Créer une notification pour le destinataire
        Notification.objects.create(
            user=receiver,
            message=message,
            is_read=False
        )
        
        messages.success(request, "Message sent successfully.")
    
    return redirect('messaging:conversation', user_id=user_id)
