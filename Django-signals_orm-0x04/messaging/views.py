from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
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
