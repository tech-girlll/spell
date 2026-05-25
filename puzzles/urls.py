from django.urls import path

from . import views

app_name = "puzzles"

urlpatterns = [
    path("play/", views.play, name="play"),
    path("round/", views.round_summary, name="round_summary"),
]