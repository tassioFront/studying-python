from django.urls import include, path

from . import views, views_internal

internal_patterns = [
    path(
        "by-email/<str:email>/", views_internal.get_user_by_email, name="user-by-email"
    ),
    path(
        "register/", views_internal.UserRegistrationView.as_view(), name="user-register"
    ),
    # Add more internal endpoints here
]

urlpatterns = [
    # Teammate-managed user endpoints (require teammate authentication)
    path("", views.UserListCreateView.as_view(), name="user-list-create"),
    path("<uuid:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    # User self-service authentication endpoints
    path("login/", views.UserLoginView.as_view(), name="user-login"),
    path(
        "set-password/",
        views.UserSetInitialPasswordView.as_view(),
        name="user-set-initial-password",
    ),
    # User self-service profile endpoints (require user authentication)
    path("me/", views.UserProfileView.as_view(), name="user-profile"),
    path(
        "me/password/",
        views.UserPasswordUpdateView.as_view(),
        name="user-password-update",
    ),
    # Inter-service communication
    path("validate-token/", views.validate_user_token, name="user-validate-token"),
    # Internal: Get user by email (path param)
    path("internal/", include((internal_patterns, "users"), namespace="internal")),
]
