from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Ajout de champs CharField pour validation
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'bio', 'avatar', 'last_seen', 'password', 'confirm_password']
        read_only_fields = ['last_seen', 'user_id']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        """Validation personnalisée avec ValidationError"""
        if 'password' in attrs and 'confirm_password' in attrs:
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Validation de l'email
        if 'email' in attrs:
            email = attrs['email']
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        
        return attrs
    
    def create(self, validated_data):
        # Supprimer confirm_password avant la création
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at', 'is_read']
        read_only_fields = ['sent_at', 'message_id']
    
    def validate_message_body(self, value):
        """Validation du contenu du message"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le message ne peut pas être vide.")
        if len(value) > 1000:
            raise serializers.ValidationError("Le message ne peut pas dépasser 1000 caractères.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    participant_emails = serializers.CharField(write_only=True, required=False, help_text="Emails des participants séparés par des virgules")
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'last_message', 
                 'created_at', 'updated_at', 'participant_emails']
        read_only_fields = ['created_at', 'updated_at', 'conversation_id']
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def validate_participant_emails(self, value):
        """Validation des emails des participants"""
        if not value:
            return value
            
        emails = [email.strip() for email in value.split(',')]
        for email in emails:
            if not serializers.EmailField().run_validation(email):
                raise serializers.ValidationError(f"Email invalide: {email}")
        
        return value
    
    def create(self, validated_data):
        participant_emails = validated_data.pop('participant_emails', '')
        conversation = Conversation.objects.create()
        
        if participant_emails:
            emails = [email.strip() for email in participant_emails.split(',')]
            users = User.objects.filter(email__in=emails)
            if users.count() != len(emails):
                found_emails = list(users.values_list('email', flat=True))
                missing_emails = set(emails) - set(found_emails)
                raise serializers.ValidationError(f"Utilisateurs non trouvés pour les emails: {', '.join(missing_emails)}")
            
            conversation.participants.set(users)
        
        return conversation