from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

class MessageHistory(models.Model):
    """Model to store historical versions of edited messages."""
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='history'
    )
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message history'
    
    def __str__(self):
        return f"Version of {self.message} from {self.edited_at}"


class Message(models.Model):
    """Model representing a message between users."""
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
    edited_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        # Check if this is an update to an existing message
        if self.pk:
            old_message = Message.objects.get(pk=self.pk)
            if old_message.content != self.content:
                # If content changed, create history entry before saving
                MessageHistory.objects.create(
                    message=self,
                    content=old_message.content
                )
                self.is_edited = True
                self.edited_at = timezone.now()
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('message-detail', kwargs={'pk': self.pk})
    
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
