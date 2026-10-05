from .context import set_current_audit_context, reset_current_audit_context


class AuditLogMiddleware:
    """
    Har bir HTTP so'rov paytida mijoz ma'lumotlarini (User, IP, MAC ID, User Agent)
    contextvars orqali signal handlerlariga yetkazib beruvchi middleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = set_current_audit_context({'request': request})
        try:
            response = self.get_response(request)
            return response
        finally:
            reset_current_audit_context(token)
