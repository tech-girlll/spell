"""
Dashboard queries.

Pulls together stats from progress (streak, points) and puzzles (results)
into a single summary for the dashboard view.
"""
from django.db.models import Avg, Count, Q

from progress.models import Streak
from puzzles.models import PuzzleResult


def get_dashboard_stats(user) -> dict:
    """All the numbers the dashboard screen needs, in one dict."""
    streak = Streak.objects.filter(user=user).first()

    results = PuzzleResult.objects.filter(user=user)
    totals = results.aggregate(
        total_played=Count("id"),
        total_solved=Count("id", filter=Q(solved=True)),
        avg_guesses=Avg("guesses_used", filter=Q(solved=True)),
    )

    total_played = totals["total_played"] or 0
    total_solved = totals["total_solved"] or 0
    accuracy = round((total_solved / total_played) * 100) if total_played else 0
    avg_guesses = round(totals["avg_guesses"], 1) if totals["avg_guesses"] else 0

    return {
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0,
        "total_points": streak.total_points if streak else 0,
        "total_played": total_played,
        "total_solved": total_solved,
        "accuracy": accuracy,
        "avg_guesses": avg_guesses,
        "rival": get_rival(user, streak),
    }


def get_rival(user, streak) -> dict | None:
    """
    The "next ahead" rival: the player directly above this user in points.

    Returns None if the user is at the top (or has no streak row yet).
    """
    my_points = streak.total_points if streak else 0

    rival_streak = (
        Streak.objects.filter(total_points__gt=my_points)
        .exclude(user=user)
        .order_by("total_points")
        .select_related("user")
        .first()
    )
    if rival_streak is None:
        return None

    return {
        "username": rival_streak.user.username,
        "points": rival_streak.total_points,
        "gap": rival_streak.total_points - my_points,
        "initial": rival_streak.user.username[0].upper(),
    }