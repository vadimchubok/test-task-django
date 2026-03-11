from django.urls import path
from app.views import BookingView


urlpatterns = [
    path("", BookingView.as_view()),
]
