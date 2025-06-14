from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Q, F

User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """
    Gestionnaire personnalisé pour les messages non lus.
    """
    def for_user(self, user):
        """
        Retourne les messages non lus pour un utilisateur donné.
        Utilise only() pour optimiser les requêtes en ne récupérant que les champs nécessaires.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id', 'content', 'timestamp', 'sender__id', 'sender__username'
        ).order_by('-timestamp')
    
    def unread_count_for_user(self, user):
        """
        Retourne le nombre de messages non lus pour un utilisateur.
        Utilise values() et count() pour une requête plus légère.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).values('id').count()
    
    def mark_as_read(self, message_ids, user):
        """
        Marque les messages comme lus.
        Utilise update() pour une mise à jour en masse plus efficace.
        """
        return self.get_queryset().filter(
            id__in=message_ids,
            receiver=user,
            is_read=False
        ).update(is_read=True)


class MessageHistory(models.Model):
    """Model pour stocker l'historique des modifications des messages."""
    original_message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='history_entries'
    )
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='message_edits'
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message Histories'

    def __str__(self):
        return f"Version of {self.original_message.id} from {self.edited_at}"

class Message(models.Model):
    """Model representing a message between users."""
    # Gestionnaires
    objects = models.Manager()  # Le gestionnaire par défaut
    unread_objects = UnreadMessagesManager()  # Notre gestionnaire personnalisé
    
    # Champs du modèle
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(
        default=False,
        help_text="Indique si le message a été lu par le destinataire"
    )
    is_edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'is_read']),  # Pour optimiser les requêtes de messages non lus
            models.Index(fields=['sender', 'receiver']),   # Pour les conversations
        ]
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='Message parent'
    )
    
    # Pour optimiser les requêtes récursives
    _thread_depth = models.PositiveIntegerField(default=0, editable=False)
    
    def save(self, *args, **kwargs):
        # Calculer la profondeur du fil de discussion
        if self.parent_message:
            self._thread_depth = self.parent_message._thread_depth + 1
        super().save(*args, **kwargs)
    
    @property
    def is_thread(self):
        """Vérifie si le message a des réponses"""
        return self.replies.exists()
    
    @classmethod
    def get_thread(cls, message_id):
        """Récupère un message avec tous ses réponses de manière optimisée"""
        from django.db.models import Prefetch
        
        return cls.objects.select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver')
                                 .order_by('timestamp'),
                to_attr='thread_replies'
            )
        ).get(pk=message_id)
    
    def get_threaded_replies(self):
        """Récupère toutes les réponses de manière récursive"""
        from django.db.models import Q
        
        # Récupération de tous les messages du fil
        thread_messages = Message.objects.filter(
            Q(pk=self.pk) | 
            Q(parent_message__in=self.replies.all())
        ).select_related('sender', 'receiver')
        
        # Construction de l'arbre des réponses
        messages_dict = {msg.id: msg for msg in thread_messages}
        for msg in thread_messages:
            if msg.parent_message_id:
                parent = messages_dict[msg.parent_message_id]
                if not hasattr(parent, 'thread_replies'):
                    parent.thread_replies = []
                parent.thread_replies.append(msg)
        
        return messages_dict.get(self.id, None)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"


class Notification(models.Model):
    """Model representing a notification for a user."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"
