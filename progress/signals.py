"""
Signals that update progress automatically when game events happen.

When a PuzzleResult is created (user finishes a puzzle):
  - total_points increases by the points earned
  - the daily streak updates (continues, starts, or stays unchanged)

Views never have to remember to update progress — it just happens.
"""
import datetime as dt

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from puzzles.models import PuzzleResult

from .models import Streak


@receiver(post_save, sender=PuzzleResult)
def on_puzzle_result(sender, instance: PuzzleResult, created: bool, **kwargs):
    if not created:
        return

    streak, _ = Streak.objects.get_or_create(user=instance.user)

    # Points always accumulate
    streak.total_points += instance.points_earned

    # Streak logic: did the user already play today?
    today = timezone.localdate()
    if streak.last_active_date != today:
        if streak.last_active_date == today - dt.timedelta(days=1):
            # Played yesterday too — streak continues
            streak.current_streak += 1
        else:
            # First play ever, or a gap — streak starts fresh
            streak.current_streak = 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_active_date = today

    streak.save()