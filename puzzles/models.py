"""
Game models for Spell.

Puzzle       — a word someone has to guess.
Attempt      — one guess at a puzzle (up to 6 per puzzle per user).
PuzzleResult — the outcome (solved/failed) of one user on one puzzle.

The correct answer lives on Word.text (via the puzzle's foreign key) and is
NEVER sent to the client. The client only sees the word length, the definition,
and the colored evaluation after each guess.
"""
from django.conf import settings
from django.db import models

from words.models import Word


class Puzzle(models.Model):
    """A word someone has to guess. Built from a Word."""

    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="puzzles",
    )
    is_daily = models.BooleanField(default=False, db_index=True)
    daily_date = models.DateField(null=True, blank=True, unique=True, db_index=True)
    max_guesses = models.PositiveSmallIntegerField(default=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_daily", "daily_date"]),
        ]

    def __str__(self) -> str:
        return f"Puzzle({self.word.text})"


class PuzzleResult(models.Model):
    """One row per (user, puzzle) — created when the user finishes the puzzle."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="puzzle_results",
    )
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        related_name="results",
    )
    solved = models.BooleanField()
    guesses_used = models.PositiveSmallIntegerField()
    points_earned = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [("user", "puzzle")]
        indexes = [
            models.Index(fields=["user", "completed_at"]),
        ]


class Attempt(models.Model):
    """One guess at a puzzle. A user gets up to puzzle.max_guesses attempts."""

    # Per-letter evaluation codes returned to the client
    EVAL_CORRECT = "G"      # right letter, right position
    EVAL_PRESENT = "Y"      # right letter, wrong position
    EVAL_ABSENT = "B"       # letter not in the word

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    guess_number = models.PositiveSmallIntegerField()
    user_input = models.CharField(max_length=50)
    is_correct = models.BooleanField()
    evaluation = models.CharField(
        max_length=50,
        help_text="String of G/Y/B per letter (e.g., 'GGYBB' for receive guessed as 'recent').",
    )
    attempted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "attempted_at"]),
            models.Index(fields=["user", "puzzle"]),
        ]