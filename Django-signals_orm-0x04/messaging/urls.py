from django.urls import path
from . import views
from .thread_views import thread_detail, reply_to_message

app_name = 'messaging'

urlpatterns = [
    # User account
    path('user/delete/', views.delete_user, name='delete_user'),
    
    # Threaded conversations
    path('thread/<int:message_id>/', thread_detail, name='thread_detail'),
    path('thread/<int:message_id>/reply/', reply_to_message, name='reply_to_message'),
    
    # Add other URLs as needed
]
