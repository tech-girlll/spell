from django.contrib import admin

from .models import Attempt, Puzzle, PuzzleResult


@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ("word", "is_daily", "daily_date", "max_guesses", "created_at")
    list_filter = ("is_daily",)
    search_fields = ("word__text",)


@admin.register(PuzzleResult)
class PuzzleResultAdmin(admin.ModelAdmin):
    list_display = ("user", "puzzle", "solved", "guesses_used", "points_earned", "completed_at")
    list_filter = ("solved",)
    search_fields = ("user__username", "puzzle__word__text")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "puzzle", "guess_number", "is_correct", "user_input", "evaluation", "attempted_at")
    list_filter = ("is_correct", "guess_number")
    search_fields = ("user__username", "puzzle__word__text")