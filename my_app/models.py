# your_app/models.py
from django.db import models

class ScrapedArticle(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True) 
    source = models.CharField(max_length=100)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title