import datetime
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class SessionIdleTimeout(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.session_key:
            return  # No session, nothing to check

        current_time = datetime.datetime.now()
        timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 1800)  # 30 min default

        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed_time = (current_time - datetime.datetime.fromisoformat(last_activity)).total_seconds()
            if elapsed_time > timeout:
                request.session.flush()  # clear session and force login
                return

        # Update last activity time on every request
        request.session['last_activity'] = current_time.isoformat()
