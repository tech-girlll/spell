from django.db import models
class Word(models.Model):
    """An English word that can become a puzzle."""

    DIFFICULTY_CHOICES = [
        (1, "Very easy"),
        (2, "Easy"),
        (3, "Medium"),
        (4, "Hard"),
        (5, "Very hard"),
    ]

    # The word itself
    text = models.CharField(max_length=50, unique=True, db_index=True)
    length = models.PositiveSmallIntegerField(
        help_text="Letter count, set automatically on save.",
    )
    difficulty_level = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES,
        default=3,
        db_index=True,
    )

    # Cached dictionary API data — populated lazily, never re-fetched
    definition = models.TextField(blank=True)
    part_of_speech = models.CharField(max_length=20, blank=True)
    example_sentence = models.TextField(blank=True)
    audio_url = models.URLField(blank=True)
    phonetic = models.CharField(max_length=100, blank=True)

    # Bookkeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["difficulty_level", "length"]),
        ]

    def __str__(self) -> str:
        return self.text

    def save(self, *args, **kwargs):
        self.text = self.text.lower()
        self.length = len(self.text)
        super().save(*args, **kwargs)
