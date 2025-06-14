from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('user/delete/', views.delete_user, name='delete_user'),
    # Add other URLs as needed
]
