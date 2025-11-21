from django.utils.deprecation import MiddlewareMixin

class RequestMetaMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # get IP (simple approach — if behind reverse proxy, use X-Forwarded-For properly)
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            request.client_ip = xff.split(",")[0].strip()
        else:
            request.client_ip = request.META.get("REMOTE_ADDR")
        request.user_agent = request.META.get("HTTP_USER_AGENT", "")
