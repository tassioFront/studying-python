from django.urls import path

from .views import ProfileView, RegisterView

# Admin/teammate management endpoints
urlpatterns = [
    path("register/", RegisterView.as_view(), name="teammate_register"),
    path("me/", ProfileView.as_view(), name="teammate_profile"),
]
