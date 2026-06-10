from django.urls import path

from . import views

app_name = "puzzles"

urlpatterns = [
    path("play/", views.play, name="play"),
    path("daily/", views.daily, name="daily"),
    path("round/", views.round_summary, name="round_summary"),
]

