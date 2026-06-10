"""
Game views.

play(request)          — renders the play screen and handles guess submissions.
round_summary(request) — shows all 10 words from the most recently finished round.

A "round" is 10 finished puzzles in a row. After the 10th finishes, the next
"Next word →" click goes to the round summary instead of a new puzzle.

Notes:
- The correct answer is NEVER passed to the play template until the puzzle is
  finished. Round summary shows all answers since the round is over.
- Business logic lives in services.py. Views just orchestrate.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from progress.models import Streak
from words.models import Word

from .models import Attempt, Puzzle, PuzzleResult
from .services import (
    calculate_points,
    evaluate_guess,
    get_or_create_daily_puzzle,
    is_valid_guess,
)


ROUND_SIZE = 10


@login_required
def play(request):
    """Render the play screen, or process a guess submission."""
    puzzle = _get_or_create_puzzle_for_user(request)

    if request.method == "POST":
        return _process_guess(request, puzzle)

    return _render_play(request, puzzle)


@login_required
def round_summary(request):
    """Show all words from the most recently finished round."""
    puzzle_ids = request.session.get("last_round_puzzle_ids", [])
    if not puzzle_ids:
        return redirect("puzzles:play")

    # Pull puzzles in the order they were played
    puzzles_by_id = {p.id: p for p in Puzzle.objects.filter(id__in=puzzle_ids)}
    results_by_puzzle = {
        r.puzzle_id: r
        for r in PuzzleResult.objects.filter(user=request.user, puzzle_id__in=puzzle_ids)
    }

    round_words = []
    for pid in puzzle_ids:
        puzzle = puzzles_by_id.get(pid)
        if not puzzle:
            continue
        result = results_by_puzzle.get(pid)
        round_words.append({
            "word": puzzle.word.text,
            "solved": result.solved if result else False,
            "guesses_used": result.guesses_used if result else 0,
            "points_earned": result.points_earned if result else 0,
            "definition": puzzle.word.definition,
            "audio_url": puzzle.word.audio_url,
            "example_sentence": puzzle.word.example_sentence,
            "part_of_speech": puzzle.word.part_of_speech,
        })

    solved_count = sum(1 for w in round_words if w["solved"])
    total_points = sum(w["points_earned"] for w in round_words)

    context = {
        "round_words": round_words,
        "solved_count": solved_count,
        "total_count": len(round_words),
        "total_points": total_points,
    }
    return render(request, "puzzles/round_summary.html", context)
@login_required
def daily(request):
    """Today's shared daily puzzle — same word for every player."""
    puzzle = get_or_create_daily_puzzle()
    if puzzle is None:
        messages.error(request, "No words available for today's puzzle.")
        return redirect("puzzles:play")

    if request.method == "POST":
        return _process_daily_guess(request, puzzle)

    return _render_daily(request, puzzle)


def _render_daily(request, puzzle: Puzzle):
    """Render the daily puzzle page."""
    attempts = Attempt.objects.filter(
        user=request.user,
        puzzle=puzzle,
    ).order_by("guess_number")

    result = PuzzleResult.objects.filter(user=request.user, puzzle=puzzle).first()
    streak = Streak.objects.filter(user=request.user).first()

    context = {
        "puzzle_id": puzzle.id,
        "word_length": puzzle.word.length,
        "definition": puzzle.word.definition,
        "max_guesses": puzzle.max_guesses,
        "attempts": attempts,
        "result": result,
        "guesses_remaining": puzzle.max_guesses - attempts.count(),
        "current_streak": streak.current_streak if streak else 0,
        "total_points": streak.total_points if streak else 0,
        "daily_date": puzzle.daily_date,
        "reveal_word": puzzle.word.text if result else None,
        "reveal_audio": puzzle.word.audio_url if result else None,
        "reveal_example": puzzle.word.example_sentence if result else None,
        "reveal_pos": puzzle.word.part_of_speech if result else None,
    }
    return render(request, "puzzles/daily.html", context)


def _process_daily_guess(request, puzzle: Puzzle):
    """Validate, evaluate, and record a guess on the daily puzzle."""
    guess = request.POST.get("guess", "").strip().lower()

    if PuzzleResult.objects.filter(user=request.user, puzzle=puzzle).exists():
        messages.error(request, "You've already played today's puzzle. Come back tomorrow!")
        return redirect("puzzles:daily")

    ok, error = is_valid_guess(guess, expected_length=puzzle.word.length)
    if not ok:
        messages.error(request, error)
        return redirect("puzzles:daily")

    existing_attempts = Attempt.objects.filter(user=request.user, puzzle=puzzle).count()
    if existing_attempts >= puzzle.max_guesses:
        messages.error(request, "No guesses remaining.")
        return redirect("puzzles:daily")

    evaluation = evaluate_guess(guess, puzzle.word.text)
    is_correct = guess == puzzle.word.text.lower()

    Attempt.objects.create(
        user=request.user,
        puzzle=puzzle,
        guess_number=existing_attempts + 1,
        user_input=guess,
        is_correct=is_correct,
        evaluation=evaluation,
    )

    guesses_used = existing_attempts + 1
    if is_correct or guesses_used >= puzzle.max_guesses:
        PuzzleResult.objects.create(
            user=request.user,
            puzzle=puzzle,
            solved=is_correct,
            guesses_used=guesses_used,
            points_earned=calculate_points(is_correct, guesses_used),
        )

    return redirect("puzzles:daily")

def _render_play(request, puzzle: Puzzle):
    """Render the play page with current puzzle state."""
    attempts = Attempt.objects.filter(
        user=request.user,
        puzzle=puzzle,
    ).order_by("guess_number")

    result = PuzzleResult.objects.filter(user=request.user, puzzle=puzzle).first()

    # How many puzzles have been finished in this round so far?
    round_progress = len(request.session.get("current_round_puzzle_ids", []))

    context = {
        "puzzle_id": puzzle.id,
        "word_length": puzzle.word.length,
        "definition": puzzle.word.definition,
        "max_guesses": puzzle.max_guesses,
        "attempts": attempts,
        "result": result,
        "guesses_remaining": puzzle.max_guesses - attempts.count(),
        "round_progress": round_progress,
        "round_size": ROUND_SIZE,
        # Reveal data is only included once the puzzle is finished
        "reveal_word": puzzle.word.text if result else None,
        "reveal_audio": puzzle.word.audio_url if result else None,
        "reveal_example": puzzle.word.example_sentence if result else None,
        "reveal_pos": puzzle.word.part_of_speech if result else None,
        # Show "Round complete" if this was the final puzzle of the round
        "round_complete": result and round_progress >= ROUND_SIZE,
    }
    return render(request, "puzzles/play.html", context)


def _process_guess(request, puzzle: Puzzle):
    """Validate, evaluate, and record a single guess. Or start a new puzzle."""

    # "Next word" button — clear session puzzle so a fresh one is picked
    if request.POST.get("next_puzzle"):
        request.session.pop("current_puzzle_id", None)

        # If the round just finished, redirect to summary instead
        round_ids = request.session.get("current_round_puzzle_ids", [])
        if len(round_ids) >= ROUND_SIZE:
            # Save this round for the summary view, then reset
            request.session["last_round_puzzle_ids"] = round_ids
            request.session["current_round_puzzle_ids"] = []
            return redirect("puzzles:round_summary")

        return redirect("puzzles:play")

    guess = request.POST.get("guess", "").strip().lower()

    # Refuse guesses on already-finished puzzles
    if PuzzleResult.objects.filter(user=request.user, puzzle=puzzle).exists():
        messages.error(request, "This puzzle is already finished.")
        return redirect("puzzles:play")

    # Validate
    ok, error = is_valid_guess(guess, expected_length=puzzle.word.length)
    if not ok:
        messages.error(request, error)
        return redirect("puzzles:play")

    # Count existing attempts for guess_number
    existing_attempts = Attempt.objects.filter(user=request.user, puzzle=puzzle).count()
    if existing_attempts >= puzzle.max_guesses:
        messages.error(request, "No guesses remaining.")
        return redirect("puzzles:play")

    # Evaluate and save the attempt
    evaluation = evaluate_guess(guess, puzzle.word.text)
    is_correct = guess == puzzle.word.text.lower()

    Attempt.objects.create(
        user=request.user,
        puzzle=puzzle,
        guess_number=existing_attempts + 1,
        user_input=guess,
        is_correct=is_correct,
        evaluation=evaluation,
    )

    # If the puzzle is done, create the PuzzleResult and add it to the round
    guesses_used = existing_attempts + 1
    if is_correct or guesses_used >= puzzle.max_guesses:
        PuzzleResult.objects.create(
            user=request.user,
            puzzle=puzzle,
            solved=is_correct,
            guesses_used=guesses_used,
            points_earned=calculate_points(is_correct, guesses_used),
        )
        # Add this puzzle to the round
        round_ids = request.session.get("current_round_puzzle_ids", [])
        if puzzle.id not in round_ids:
            round_ids.append(puzzle.id)
        request.session["current_round_puzzle_ids"] = round_ids

    return redirect("puzzles:play")


def _get_or_create_puzzle_for_user(request) -> Puzzle:
    """
    Get the user's current puzzle, sticking with it across requests.

    Uses the session to remember which puzzle the user is currently playing.
    Stays on the puzzle even after it's finished, so the reveal screen
    can be shown. The user clicks "Next word" to clear it and move on.
    """
    user = request.user
    current_id = request.session.get("current_puzzle_id")

    if current_id:
        puzzle = Puzzle.objects.filter(id=current_id).first()
        if puzzle:
            return puzzle

    # No current puzzle — pick a new word the user hasn't played
    word = (
        Word.objects.exclude(definition="")
        .exclude(puzzles__results__user=user)
        .order_by("?")
        .first()
    )
    if word is None:
        word = Word.objects.exclude(definition="").order_by("?").first()

    puzzle = Puzzle.objects.create(word=word)
    request.session["current_puzzle_id"] = puzzle.id
    return puzzle