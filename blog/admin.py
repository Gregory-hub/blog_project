from django.contrib import admin

from .models import *

class ArticleAdmin(admin.ModelAdmin):
    ordering = ['-pub_date']
    date_hierarchy = 'pub_date'
    list_filter = ['tag', 'pub_date', 'last_edit', ('author', admin.RelatedOnlyFieldListFilter)]
    readonly_fields = ['author', 'pub_date', 'last_edit']
    search_fields = ['name', 'author__name', 'tag__name']


class WriterAdmin(admin.ModelAdmin):
    list_filter = ['age']
    search_fields = ['name', 'age']


class CommentAdmin(admin.ModelAdmin):
    list_filter = [
        'comment_date',
        ('author', admin.RelatedOnlyFieldListFilter),
        ('article', admin.RelatedOnlyFieldListFilter)
    ]
    date_hierarchy = 'comment_date'
    ordering = ['-comment_date']
    readonly_fields = ['author', 'comment_date']
    search_fields = ['author__name', 'article__name', 'text']


admin.site.register(Tag)
admin.site.register(Writer, WriterAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
