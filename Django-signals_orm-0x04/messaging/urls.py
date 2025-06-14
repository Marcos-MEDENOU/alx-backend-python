from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('account/delete/', views.delete_account, name='delete_account'),
    # Add other URLs as needed
]
