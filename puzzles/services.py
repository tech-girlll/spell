"""
Game logic for Spell.

This module is the brain of the game. It handles:
  - Creating Puzzles from Words.
  - Validating guesses (length, letters only, real word).
  - Evaluating guesses (the green/yellow/grey logic).
  - Scoring (points based on guess count).

Everything here runs server-side. The correct answer is never returned
to the client — only the evaluation pattern is.
"""
from typing import Optional

from words.models import Word

from .models import Attempt, Puzzle


# Scoring: more points for solving in fewer guesses
POINTS_BY_GUESS_COUNT = {
    1: 60,
    2: 50,
    3: 40,
    4: 30,
    5: 20,
    6: 10,
}
POINTS_ON_FAIL = 0


# ----------------------------------------------------------------------------
# Puzzle creation
# ----------------------------------------------------------------------------

def create_puzzle_from_word(word: Word, is_daily: bool = False, daily_date=None) -> Puzzle:
    """Create a Puzzle from a Word. Doesn't pick the word — caller does."""
    return Puzzle.objects.create(
        word=word,
        is_daily=is_daily,
        daily_date=daily_date,
    )


# ----------------------------------------------------------------------------
# Guess validation
# ----------------------------------------------------------------------------

def is_valid_guess(guess: str, expected_length: int) -> tuple[bool, str]:
    """
    Validate a guess before evaluating it.

    Returns (is_valid, error_message). The error_message is empty on success.

    Checks:
      - Non-empty
      - Letters only (a-z)
      - Correct length
      - Optional: is a real word (we check against our Word table)
    """
    if not guess:
        return False, "Guess cannot be empty."

    guess = guess.lower()

    if not guess.isalpha():
        return False, "Guess must contain only letters."

    if len(guess) != expected_length:
        return False, f"Guess must be {expected_length} letters long."

    # Optional: enforce that the guess is a real word in our database.
    # Commented out for now — would block valid English words we haven't seeded.
    # Uncomment when our Word table is large enough.
    # if not Word.objects.filter(text=guess).exists():
    #     return False, "Not a word in our dictionary."

    return True, ""


# ----------------------------------------------------------------------------
# Guess evaluation — the heart of the game
# ----------------------------------------------------------------------------

def evaluate_guess(guess: str, target: str) -> str:
    """
    Compare a guess to the target word and return the colored evaluation.

    Returns a string of characters where each position is:
      'G' — right letter, right position (green)
      'Y' — right letter, wrong position (yellow)
      'B' — letter not in the word (grey/black)

    Handles duplicate letters correctly: greens are assigned first, then
    yellows can only "claim" letters in the target that weren't already
    matched. This is the Wordle rule.

    Example:
        evaluate_guess("llama", "allow")  ->  "YGYBB"
    """
    guess = guess.lower()
    target = target.lower()
    length = len(target)

    result = [Attempt.EVAL_ABSENT] * length

    # Step 1: mark all exact matches as green, and track which target
    # positions have been "consumed" so we don't double-count them.
    target_remaining = list(target)
    for i in range(length):
        if guess[i] == target[i]:
            result[i] = Attempt.EVAL_CORRECT
            target_remaining[i] = None  # consumed

    # Step 2: for non-green positions, mark yellow if the letter still
    # exists in the remaining target. Each letter can only be claimed once.
    for i in range(length):
        if result[i] == Attempt.EVAL_CORRECT:
            continue
        if guess[i] in target_remaining:
            result[i] = Attempt.EVAL_PRESENT
            # Remove the first matching letter from remaining
            target_remaining[target_remaining.index(guess[i])] = None

    return "".join(result)


# ----------------------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------------------

def calculate_points(solved: bool, guesses_used: int) -> int:
    """Points earned for finishing a puzzle."""
    if not solved:
        return POINTS_ON_FAIL
    return POINTS_BY_GUESS_COUNT.get(guesses_used, POINTS_ON_FAIL)