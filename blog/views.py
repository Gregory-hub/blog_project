import random
import datetime
import string
import os

from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage

from .models import Article, Writer
from .forms import *


def upload_file(dest, file):
    filename = default_storage.get_available_name(os.path.join(dest, file.name))
    with open(filename, 'wb+') as dest:
        for c in file.chunks():
            dest.write(c)
    return filename


def render_empty_form(request, form, template, message=''):
    context = {
        'message': message,
        'form': form,
    }
    return render(request, template, context)


def index(request):
    if Article.objects.count() >= 17:
        articles_init = Article.objects.order_by('-pub_date')[17]
    else:
        articles_init = list(Article.objects.order_by('-pub_date'))

    comments_nums = []
    for article in articles_init:
        comments_nums.append(article.comment_set.count())

    articles_old = []
    for i in range(len(comments_nums)):
        articles_old.append(articles_init.pop(max(comments_nums)))
    print(articles_old)

    article1 = articles_old.pop(0)
    articles = []
    while len(articles_old) > 1:
        if 2 <= len(articles_old) <= 3:
            articles.append([random.randint(1, 3), articles_old])
            articles_old = []
        mode = random.randint(1, 4)
        if mode == 4:
            articles.append([mode, articles_old[:3]])
            articles_old = articles_old[3:]
        else:
            articles.append([mode, articles_old[:2]])
            articles_old = articles_old[2:]
        print(articles)

    context = {
        'article1': article1,
        'articles': articles,
        'authenticated': request.user.is_authenticated
    }
    print(context)

    template = 'blog/blog_index.html'
    return render(request, template, context)


def article(request, writer_name, article_name):
    template = 'blog/article.html'

    writer = get_object_or_404(Writer, name=writer_name)
    article = get_object_or_404(Article, name=article_name)

    recommended_article = writer.article_set.exclude(name=article.name).order_by('-pub_date')[0]

    form = CommentForm()

    context = {
        'article': article,
        'form': form,
        'recommended_article': recommended_article,
        'comments': Comment.objects.filter(article=article),
        'message': '',
    }

    if request.method == 'GET':
        return render(request, template, context)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            context['message'] = 'You must login to comment'
            return render(request, template, context)

        form = CommentForm(request.POST)

        if form.is_valid():

            author = get_object_or_404(Writer, name=request.user.username)
            text = form.cleaned_data['text']
            comment_date = timezone.now()

            article.comment_set.create(
                author = author,
                text = text,
                comment_date = comment_date,
            )
            return HttpResponseRedirect(reverse('blog:article', args=(writer_name, article_name)))
        else:
            context['message'] = 'Form is invalid'
            return render(request, template, context)


def writer(request, writer_name):
    template = 'blog/writer.html'
    writer = get_object_or_404(Writer, name=writer_name)

    articles = list(writer.article_set.order_by('-pub_date'))
    if articles == []:
        message = 'No articles'
    else:
        message = ''

    context = {
        'message': message,
        'name': writer.name,
        'articles': articles,
    }
    return render(request, template, context)


def my_page(request):
    template = 'blog/my_page.html'
    if not request.user.is_authenticated:
        return HttpResponse('<h1>401 unauthorized</h1>', status=401)

    try:
        writer = Writer.objects.get(name=request.user.username)
    except Writer.DoesNotExist:
        return HttpResponseRedirect(reverse('blog:index'))

    articles = list(writer.article_set.order_by('-pub_date'))
    if articles == []:
        message = 'No articles'
    else:
        message = ''

    types = []
    for i in range(len(articles)):
        types.append(articles.index(articles[i]) % 4)
    articles = dict(zip(articles, types))

    add_form = AddForm()
    image_form = WriterImageForm()
    bio_form = WriterBioForm(initial={'age': writer.age, 'bio': writer.bio})


    context = {
        'message': message,
        'writer': writer,
        'image_form': image_form,
        'bio_form': bio_form,
        'add_form': add_form,
        'articles': articles,
    }

    if request.method == 'GET':
        return render(request, template, context)

    elif request.method == 'POST':
        print(request.POST)

        if 'bio_form' in request.POST:

            # writer bio form

            bio_form = WriterBioForm(request.POST, instance=writer)
            if bio_form.is_valid:
                bio_form.save()
                return HttpResponseRedirect(reverse('blog:my_page'))
            else:
                context['message'] = 'Form is invalid'
                return render(request, template, context)

        elif 'add_form' in request.POST:

            # add article form

            add_form = AddForm(request.POST, request.FILES)

            if add_form.is_valid():
                tag_name = add_form.cleaned_data['tag']

                name = add_form.cleaned_data['name']
                text = add_form.cleaned_data['text']
                tag = Tag.objects.get(name=tag_name)
                writer = Writer.objects.get(name=request.user.username)

                imagename = upload_file('media/articles/images/', request.FILES['image'])

                if list(writer.article_set.filter(name=name)) == []:

                    writer.article_set.create(
                        name = name,
                        text = text,
                        image = imagename,
                        tag = tag,
                        pub_date = timezone.now(),
                        last_edit = timezone.now(),
                    )

                    return HttpResponseRedirect(reverse('blog:my_page'))
                else:
                    context['message'] = 'This name is not available'
                    return render(request, template, context)
            else:
                return render_empty_form(request, form, template, 'Form is invalid')

        elif 'image_form' in request.POST:

            # writer image form

            image_form = WriterImageForm(request.POST, request.FILES, instance=writer)
            if image_form.is_valid:
                if request.FILES['image'] != '':
                    image_form.save()
                    return HttpResponseRedirect(reverse('blog:my_page'))
            else:
                context['message'] = 'Form is invalid'
                return render(request, template, context)


def my_article(request, article_name):
    template = 'blog/my_article.html'
    if not request.user.is_authenticated:
        return HttpResponse('<h1>401 unauthorized</h1>', status=401)

    if request.method == 'GET':
        writer = get_object_or_404(Writer, name=request.user.username)
        article = writer.article_set.get(name=article_name)

        context = {
            'author': article.author,
            'name': article.name,
            'text': article.text,
            'tag': article.tag,
            'pub_date': article.pub_date,
            'last_edit': article.last_edit,
            'comments': Comment.objects.filter(article=article),
            'form1': DeleteButton,
            'form2': EditButton,
        }
        return render(request, template, context)

    elif request.method == 'POST':
        writer = get_object_or_404(Writer, name=request.user.username)
        article = writer.article_set.get(name=article_name)

        if request.POST['value'] == 'delete':
            form = DeleteButton(request.POST)
            if form.is_valid:
                article.delete()
            else:
                return HttpResponseRedirect(reverse('blog:my_article', args=(article_name, )))

        elif request.POST['value'] == 'edit':
            form = EditButton(request.POST)
            if form.is_valid:
                return HttpResponseRedirect(reverse('blog:edit', args=(article_name, )))
            else:
                return HttpResponseRedirect(reverse('blog:my_article', args=(article_name, )))

        return HttpResponseRedirect(reverse('blog:my_page'))


def add(request):
    template = 'blog/add.html'

    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('blog:index'))

    if request.method == 'GET':
        form = AddForm()
        return render_empty_form(request, form, 'blog/add.html')

    elif request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            text = form.cleaned_data['text']
            tag_name = form.cleaned_data['tag']

            tag = get_object_or_404(Tag, name=tag_name)
            writer = Writer.objects.get(name=user.username)

            if list(writer.article_set.filter(name=name)) == []:
                writer.article_set.create(
                    author=writer,
                    name=name,
                    text = text,
                    tag = tag,
                    pub_date=timezone.now(),
                    last_edit=timezone.now(),
                )
                return HttpResponseRedirect(reverse('blog:my_page'))
            else:
                return render_empty_form(request, form, template, "This name is not available")
        else:
            return render_empty_form(request, form, template, 'Form is invalid')


def edit(request, article_name):
    template = 'blog/edit.html'

    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('blog:index'))

    if request.method == 'GET':
        context = {
            'article_name': article_name,
            'message': '',
            'form': EditForm(),
        }
        return render(request, template, context)

    elif request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            text = form.cleaned_data['text']
            writer = Writer.objects.get(name=user.username)

            if list(writer.article_set.filter(name=name)) == []:
                article = writer.article_set.get(name=article_name)
                if name != '':
                    article.name = name
                if text != '':
                    article.text = text
                article.last_edit=timezone.now()
                article.save()
                return HttpResponseRedirect(reverse('blog:my_article', args=(article.name, )))
            else:
                context = {
                    'article_name': article_name,
                    'message': 'This name is not available',
                    'form': EditForm(),
                }
                return render(request, template, context)
        else:
            context = {
                'article_name': article_name,
                'message': 'Form is invalid',
                'form': EditForm(),
            }
            return render(request, template, context)


def login(request):
    template = 'blog/login.html'
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('blog:index'))

    if request.method == 'GET':
        form = LogInForm()
        return render_empty_form(request, form, template)

    elif request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('blog:index'))
            else:
                if list(User.objects.filter(username=username)) == []:
                    return render_empty_form(request, form, template, 'User does not exist')
                else:
                    return render_empty_form(request, form, template, 'Wrong password')
        else:
            return render_empty_form(request, form, template, 'Form is invalid')


def sign_up(request):
    template = 'blog/sign_up.html'

    if request.method == 'GET':
        form = SignUpForm()
        return render_empty_form(request, form, template)

    elif request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)

        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if list(User.objects.filter(username=username)) == []:
                User.objects.create_user(username=username, password=password)
                Writer.objects.create(name=username)

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)

                return HttpResponseRedirect(reverse('blog:index'))
            else:
                return render_empty_form(request, form, template, "This username is not available")

        else:
            return render_empty_form(request, form, template, 'Form is invalid')


def logout(request):
    if request.user.is_authenticated:
        logout(request)

    return HttpResponseRedirect(reverse('blog:index'))


def authors(request):
    return HttpResponse('Ok authors')


def tags(request):
    return HttpResponse('Ok tags')


def tag(request, tag_name):
    return HttpResponse('Ok tag')
