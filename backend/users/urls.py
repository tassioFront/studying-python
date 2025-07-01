from django.urls import path

from . import views

urlpatterns = [
    # Teammate-managed user endpoints (require teammate authentication)
    path("", views.UserListCreateView.as_view(), name="user-list-create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    # User self-service authentication endpoints
    path("register/", views.UserRegistrationView.as_view(), name="user-register"),
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
]
