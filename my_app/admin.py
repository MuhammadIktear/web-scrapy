from django.contrib import admin

# Register your models here.
from .models import ScrapedArticle

admin.site.register(ScrapedArticle)