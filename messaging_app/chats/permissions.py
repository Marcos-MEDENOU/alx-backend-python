from rest_framework import permissions

class IsParticipantOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For Conversation: check if user is a participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For Message: check if user is a participant in the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False