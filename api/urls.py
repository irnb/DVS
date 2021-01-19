from django.urls import path
from .views import Subscribe



urlpatterns = [
    path('subscribe',Subscribe.as_view()),
]
