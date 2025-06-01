from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        # Add the creator as a participant
        conversation.participants.add(self.request.user)
        # Add other participants from the request data
        participants = self.request.data.get('participants', [])
        for participant_id in participants:
            conversation.participants.add(participant_id)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Verify user is a participant
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionError("You are not a participant in this conversation")
            
        serializer.save(
            sender=self.request.user,
            conversation_id=conversation_id
        )
        
        # Update conversation timestamp
        conversation.save()  # This will update the updated_at field
