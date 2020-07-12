from django.urls import path, include
from .views import *

app_name = 'blog'
urlpatterns = [
    path('', index, name='index'),
    path('login/', log_in, name='login'),
    path('logout/', log_out, name='logout'),
    path('sign_up/', sign_up, name='sign_up'),
    path('authors', authors, name='authors'),
    path('tags', tags, name='tags'),
    path('tag/<str:tag_name>', tag, name='tag'),
    path('my_page/', my_page, name='my_page'),
    path('my_page/<str:article_name>/', my_article, name='my_article'),
    path('my_page/<str:article_name>/edit/', edit, name='edit'),
    path('my_page/<str:article_name>/delete/', delete, name='delete'),
    path('search/', search, name='search'),
    path('<str:writer_name>/', writer, name='writer'),
    path('<str:writer_name>/<str:article_name>/', article, name='article'),
]
