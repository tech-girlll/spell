"""
Seed the Word table with a starter list of words.

Usage:
    python manage.py seed_words

Safe to run multiple times — uses get_or_create so it won't duplicate.
"""
from django.core.management.base import BaseCommand

from words.models import Word


# (word, difficulty_level)
STARTER_WORDS = [
    # Very easy — 1
    ("cat", 1), ("dog", 1), ("sun", 1), ("hat", 1), ("run", 1),
    ("red", 1), ("big", 1), ("egg", 1), ("box", 1), ("cup", 1),

    # Easy — 2
    ("apple", 2), ("happy", 2), ("water", 2), ("bread", 2), ("smile", 2),
    ("table", 2), ("green", 2), ("paper", 2), ("music", 2), ("river", 2),

    # Medium — 3
    ("receive", 3), ("believe", 3), ("compute", 3), ("animal", 3), ("rhythm", 3),
    ("anxiety", 3), ("village", 3), ("forest", 3), ("travel", 3), ("planet", 3),

    # Hard — 4
    ("conscience", 4), ("necessary", 4), ("separate", 4), ("argument", 4),
    ("definitely", 4), ("occurrence", 4), ("embarrass", 4), ("knowledge", 4),
    ("vacuum", 4), ("rhetoric", 4),

    # Very hard — 5
    ("photosynthesis", 5), ("conscientious", 5), ("entrepreneur", 5),
    ("onomatopoeia", 5), ("perseverance", 5), ("sycophant", 5),
    ("obsequious", 5), ("ephemeral", 5), ("ubiquitous", 5), ("paradigm", 5),
]


class Command(BaseCommand):
    help = "Seed the database with a starter list of words."

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for text, difficulty in STARTER_WORDS:
            _, created = Word.objects.get_or_create(
                text=text.lower(),
                defaults={"difficulty_level": difficulty},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + {text}"))
            else:
                skipped_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count}, skipped {skipped_count} (already existed)."
            )
        )