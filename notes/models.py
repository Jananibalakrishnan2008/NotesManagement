from django.db import models


class Note(models.Model):
    CATEGORY_CHOICES = [
        ('Study', 'Study'),
        ('Project', 'Project'),
        ('Personal', 'Personal'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def word_count(self):
        """Returns the number of words in the note content."""
        return len(self.content.split()) if self.content else 0

    @property
    def char_count(self):
        """Returns the number of characters in the note content."""
        return len(self.content) if self.content else 0

    @property
    def reading_time(self):
        """Estimated reading time in minutes (approx 200 words per minute)."""
        words = self.word_count
        mins = max(1, round(words / 200))
        return mins