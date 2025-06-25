from django.urls import path
from .views import RegisterView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('me/', ProfileView.as_view()),
]
