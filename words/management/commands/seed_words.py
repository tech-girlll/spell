"""
Seed the Word table from a wordlist file.

The file should contain one word per line, ordered by frequency
(most common first). Frequency rank is used to grade difficulty.

Usage:
    python manage.py seed_words                      # default file, max 2000 words
    python manage.py seed_words --max 5000           # seed more
    python manage.py seed_words --file path/to.txt   # custom file
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from words.models import Word

DEFAULT_WORDLIST = Path(__file__).resolve().parent.parent.parent / "data" / "wordlist.txt"

# Filters
MIN_LENGTH = 3
MAX_LENGTH = 12


def grade_difficulty(rank: int, total: int) -> int:
    """
    Map frequency rank to difficulty 1-5.

    The most common words are easiest; the rarest are hardest.
    Cutoffs are proportional to the size of the list.
    """
    fraction = rank / total
    if fraction < 0.10:
        return 1
    if fraction < 0.30:
        return 2
    if fraction < 0.60:
        return 3
    if fraction < 0.85:
        return 4
    return 5


class Command(BaseCommand):
    help = "Seed the database with words from a frequency-ranked wordlist file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=str(DEFAULT_WORDLIST),
            help="Path to wordlist file (one word per line, frequency-ordered).",
        )
        parser.add_argument(
            "--max",
            type=int,
            default=2000,
            help="Maximum number of words to seed (after filtering).",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        max_words = options["max"]

        if not path.exists():
            raise CommandError(f"Wordlist file not found: {path}")

        raw_words = path.read_text().splitlines()
        total_raw = len(raw_words)

        # Filter junk
        candidates = []
        for w in raw_words:
            w = w.strip().lower()
            if not w.isalpha():
                continue  # skip anything with digits, hyphens, apostrophes
            if not (MIN_LENGTH <= len(w) <= MAX_LENGTH):
                continue
            candidates.append(w)
            if len(candidates) >= max_words:
                break

        self.stdout.write(
            f"Read {total_raw} lines, {len(candidates)} usable words after filtering "
            f"(letters only, {MIN_LENGTH}-{MAX_LENGTH} chars, max {max_words})."
        )

        created_count = 0
        skipped_count = 0
        total = len(candidates)

        for rank, text in enumerate(candidates):
            difficulty = grade_difficulty(rank, total)
            _, created = Word.objects.get_or_create(
                text=text,
                defaults={"difficulty_level": difficulty},
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count}, skipped {skipped_count} (already existed)."
            )
        )
        self.stdout.write(
            "Next: run 'python manage.py enrich_words --delay 1.0' to fetch dictionary data."
        )