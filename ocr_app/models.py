from django.db import models

class ProcessedFile(models.Model):
    file_hash = models.CharField(max_length=32, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_hash
