# WarmNest/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import redirect
import time

class SessionIdleTimeout(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        current_time = int(time.time())
        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed_time = current_time - last_activity
            if elapsed_time > settings.SESSION_IDLE_TIMEOUT:
                from django.contrib.auth import logout
                logout(request)
                return redirect('wguest:login')  # Replace with your login view name

        request.session['last_activity'] = current_time
