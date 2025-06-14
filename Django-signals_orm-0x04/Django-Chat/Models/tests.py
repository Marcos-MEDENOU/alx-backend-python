from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message, Notification, MessageHistory

User = get_user_model()

class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )
    
    def test_message_creation(self):
        """Test that a message can be created and has the correct string representation."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, this is a test message.'
        )
        self.assertEqual(str(message), f'Message from {self.sender} to {self.receiver} at {message.timestamp}')
        self.assertFalse(message.is_edited)
        self.assertIsNone(message.edited_at)
    
    def test_message_edit(self):
        """Test that editing a message updates the edited fields and creates history."""
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Original message'
        )
        
        # Edit the message
        original_timestamp = message.timestamp
        message.content = 'Updated message'
        message.save()
        
        # Refresh from database
        message.refresh_from_db()
        
        # Check message fields
        self.assertTrue(message.is_edited)
        self.assertIsNotNone(message.edited_at)
        self.assertEqual(message.content, 'Updated message')
        self.assertEqual(message.timestamp, original_timestamp)  # Timestamp shouldn't change
        
        # Check history was created
        self.assertEqual(message.history.count(), 1)
        history = message.history.first()
        self.assertEqual(history.content, 'Original message')
    
    def test_multiple_edits(self):
        """Test that multiple edits create multiple history entries."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='First version'
        )
        
        # First edit
        message.content = 'Second version'
        message.save()
        
        # Second edit
        message.content = 'Third version'
        message.save()
        
        # Check history
        self.assertEqual(message.history.count(), 2)
        self.assertEqual(message.history.first().content, 'Second version')
        self.assertEqual(message.history.last().content, 'First version')
    
    def test_no_history_on_other_field_updates(self):
        """Test that updating non-content fields doesn't create history."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Original message'
        )
        
        # Update is_read field
        message.is_read = True
        message.save()
        
        # Should not create history
        self.assertEqual(message.history.count(), 0)
        self.assertFalse(message.is_edited)
        self.assertIsNone(message.edited_at)


class NotificationSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )
    
    def test_notification_created_on_message_save(self):
        """Test that a notification is created when a new message is saved."""
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, this is a test message.'
        )
        
        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
    
    def test_notification_not_created_on_message_update(self):
        """Test that a notification is not created when an existing message is updated."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, this is a test message.'
        )
        
        # Clear notifications
        Notification.objects.all().delete()
        
        # Update the message
        message.content = 'Updated content'
        message.save()
        
        # Check that no new notification was created
        self.assertEqual(Notification.objects.count(), 0)
