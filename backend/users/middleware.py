from django.conf import settings
from django.http import JsonResponse

import jwt


class InternalJWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/users/internal/"):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return JsonResponse({"error": "Unauthorized"}, status=401)
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token, settings.INTERNAL_JWT_SECRET_KEY, algorithms=["HS256"]
                )
                allowed_services = getattr(
                    settings, "INTERNAL_JWT_ALLOWED_SERVICES", ["sugarfoot"]
                )
                if payload.get("service") not in allowed_services:
                    return JsonResponse({"error": "Unauthorized"}, status=401)
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=401)
        return self.get_response(request)
