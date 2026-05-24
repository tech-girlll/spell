"""
Enrich Word rows with dictionary data.

Loops through every Word that doesn't have a definition yet and fetches
the data from the Free Dictionary API. Safe to run multiple times — only
hits the API for words still missing data.

Usage:
    python manage.py enrich_words
    python manage.py enrich_words --force   # re-fetch even cached words
"""
import time

from django.core.management.base import BaseCommand

from words.models import Word
from words.services import fetch_word_data



class Command(BaseCommand):
    help = "Fetch dictionary data for words missing it."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-fetch even words that already have cached data.",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.5,
            help="Seconds to wait between API calls (be kind to the free API).",
        )

    def handle(self, *args, **options):
        force = options["force"]
        delay = options["delay"]

        if force:
            words = Word.objects.all()
        else:
            words = Word.objects.filter(definition="")

        total = words.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nothing to enrich. All words have data."))
            return

        self.stdout.write(f"Enriching {total} word(s)...\n")

        enriched = 0
        failed = 0

        for word in words:
            data = fetch_word_data(word.text)
            if data is None:
                self.stdout.write(self.style.WARNING(f"  ? {word.text}  (not found)"))
                failed += 1
            else:
                word.definition = data["definition"]
                word.part_of_speech = data["part_of_speech"]
                word.example_sentence = data["example_sentence"]
                word.audio_url = data["audio_url"]
                word.phonetic = data["phonetic"]
                word.save()
                self.stdout.write(self.style.SUCCESS(f"  + {word.text}"))
                enriched += 1

            time.sleep(delay)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Done. Enriched {enriched}, failed {failed}.")
        )