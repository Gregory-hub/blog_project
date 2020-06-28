from django.contrib import admin

from .models import Article, Writer

admin.site.register(Article)
admin.site.register(Writer)
