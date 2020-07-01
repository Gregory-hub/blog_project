import random
import datetime
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


def get_groups(article_set):
    """
    Sorts latest articles by number of comments and group them by 2 and 3
    Returned list format: [[mode, articles], [mode, articles], ...]
    mode is mode to display articles in browser
    """
    # get latest articles(max: 40)
    if len(article_set) == 0:
        return []
    if Article.objects.count() > 40:
        articles_old = article_set.order_by('-pub_date')[random.randint(20, 40)]
    else:
        articles_old = list(Article.objects.order_by('-pub_date'))

    # order articles by num of comments
    comments_nums = []
    for article in articles_old:
        comments_nums.append(article.comment_set.count())

    articles = []
    for i in range(len(comments_nums)):
        articles.append(articles_old.pop(max(comments_nums)))

    # group articles
    groups = []
    while len(articles) > 1:
        if len(articles) == 4:
            slice, articles = articles[len(articles)-2:], articles[:len(articles)-2]
            groups.append([random.randint(1, 3), slice])
        if len(articles) == 3:
            groups.append([random.randint(4, 5), articles])
            break
        elif len(articles) == 2:
            groups.append([random.randint(1, 3), articles])
            break

        mode = random.randint(1, 5)
        if 1 <= mode <= 3:
            slice, articles = articles[len(articles)-2:], articles[:len(articles)-2]
            groups.append([mode, slice])
        else:
            slice, articles = articles[len(articles)-3:], articles[:len(articles)-3]
            groups.append([mode, slice])
    return groups


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
    template = 'blog/blog_index.html'

    articles = list(Article.objects.all())
    if len(articles) > 0:
        article1 = articles.pop(0)
        groups = get_groups(articles)
    else:
        article1 = None
        groups = []

    print(*groups, sep='\n')

    context = {
        'article1': article1,
        'groups': groups,
        'authenticated': request.user.is_authenticated
    }
    return render(request, template, context)


def article(request, writer_name, article_name):
    template = 'blog/article.html'

    writer = get_object_or_404(Writer, name=writer_name)
    article = get_object_or_404(Article, name=article_name)

    if writer.article_set.exclude(name=article.name).exists():
        recommended_article = writer.article_set.exclude(name=article.name).order_by('-pub_date')[0]
    else:
        recommended_article = None

    form = CommentForm()
    context = {
        'article': article,
        'form': form,
        'recommended_article': recommended_article,
        'comments': article.comment_set.order_by('-comment_date'),
        'message': '',
        'authenticated': request.user.is_authenticated,
    }
    if not context['authenticated']:
        context['message'] = 'You cannot comment. Login to unlock this privelegy'


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

    articles = writer.article_set.order_by('-pub_date')
    if articles == []:
        message = 'No articles'
    else:
        message = ''
    authenticated = request.user.is_authenticated

    context = {
        'message': message,
        'writer': writer,
        'articles': articles,
        'authenticated': authenticated,
    }
    return render(request, template, context)


def my_page(request):
    template = 'blog/my_page.html'

    if not request.user.is_authenticated:
        return HttpResponse('<h1>401 unauthorized</h1>', status=401)

    writer = get_object_or_404(Writer, name=request.user.username)

    articles = writer.article_set.order_by('-pub_date')
    if articles == []:
        message = 'No articles'
    else:
        message = ''

    add_form = AddForm()
    image_form = WriterImageForm()
    bio_form = WriterBioForm(initial={'age': writer.age, 'bio': writer.bio})

    context = {
        'message': message,
        'writer': writer,
        'articles': articles,
        'image_form': image_form,
        'bio_form': bio_form,
        'add_form': add_form,
    }

    if request.method == 'GET':
        return render(request, template, context)

    elif request.method == 'POST':

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
                context['message'] = 'Form is invalid'
                return render(request, template, context)

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
            'article': article,
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


def log_in(request):
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
