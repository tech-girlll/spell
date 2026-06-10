from django.db import models

# Create your models here.
"""
Progress tracking for Spell.

Streak — one row per user: consecutive days played, longest run, total points.
Updated automatically via signals when a PuzzleResult is created.
"""
from django.conf import settings

class Streak(models.Model):
    """One row per user, tracking daily activity and lifetime points."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="streak",
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username}: {self.current_streak} day streak, {self.total_points} pts"