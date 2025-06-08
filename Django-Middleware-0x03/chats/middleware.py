import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request_logger')
        handler = logging.FileHandler('c:/Users/SYKO Electronics/Desktop/alx-backend-python/Django-Middleware-0x03/chats/requests.log')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        start = time(18, 0)  # 6:00 PM
        end = time(21, 0)    # 9:00 PM
        if not (start <= now <= end):
            return HttpResponseForbidden("Access to the messaging app is only allowed between 6PM and 9PM.")
        return self.get_response(request)