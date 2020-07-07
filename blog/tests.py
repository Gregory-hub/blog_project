import unittest
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout, get_user
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from .models import *
from .forms import *


def create_writer(name, age, image=None, bio=None):

    writer = Writer.objects.create(
        name = name,
        age = age,
    )
    if image:
        writer.image = image
    if bio:
        writer.bio = bio
    writer.save()

    return writer


def create_article(writer, name, text, image, tag):
    article = writer.article_set.create(
        name = name,
        text = text,
        image = image,
        tag = tag,
        pub_date = timezone.now(),
        last_edit = timezone.now()
    )
    return article


def create_tag(name, image=None):
    tag = Tag.objects.create(name=name)
    if image:
        tag.image = image
        tag.save()

    return tag


def create_user(username, password):
    user = User.objects.create_user(username=username, password=password)

    return user


@unittest.skip('done')
class IndexViewTestCase(TestCase):

    def test_status_200(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)

@unittest.skip('done')
class ArticleViewTestCase(TestCase):

    def setUp(self):
        self.user = create_user('writer0', 'writer0')
        self.writer = create_writer('writer0', 0)
        self.tag = create_tag('Tag0')
        with open(settings.MEDIA_ROOT + r'\media\test\images\test0.jpg', 'rb') as file:
            image = SimpleUploadedFile('test0.jpg', file.read(), content_type='image/jpg')
            self.article = create_article(self.writer, 'article1', 'article1 text', image, self.tag)


    def test_status_200(self):
        response = self.client.get(reverse('blog:article', args=(self.writer.name, self.article.name)))
        self.assertEqual(response.status_code, 200)


    def test_unexisting_article(self):
        response = self.client.get(reverse('blog:article', args=(self.writer.name, 'random_name')))
        self.assertEqual(response.status_code, 404)


    def test_comment_creation(self):
        username = 'commentator'
        password = 'commentator'

        commentator = create_user(username, password)
        create_writer(username, 93)
        self.client.login(username=username, password=password)

        text = 'comment text'
        response = self.client.post(
            reverse('blog:article', args=(self.writer.name, self.article.name)),
            {'text': text},
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Comment.objects.filter(article=self.article, text=text).exists())

@unittest.skip('done')
class WriterViewTests(TestCase):

    def test_status_200(self):
        writer = create_writer('writer0', 31)
        response = self.client.get(reverse('blog:writer', args=(writer.name, )))
        self.assertEqual(response.status_code, 200)

@unittest.skip('done')
class MyPageViewTests(TestCase):

    def setUp(self):
        self.tag = create_tag('No tag')
        self.user = create_user('writer0', 'writer0')
        self.writer = create_writer('writer0', 0)
        self.client.login(username='writer0', password='writer0')


    def test_get_status_200(self):
        response = self.client.get(reverse('blog:my_page'))
        self.assertEqual(response.status_code, 200)


    def test_post_add_form(self):
        name = 'article0'
        text = 'article0 text'
        tag = self.tag

        with open(settings.MEDIA_ROOT + r'\media\test\images\test1.jpg', 'rb') as image:
            image = SimpleUploadedFile('test1.jpg', image.read(), content_type='image/jpeg')
            response = self.client.post(reverse('blog:my_page'), {
                'add_form': ['Save'],
                'name': name,
                'text': text,
                'tag': tag.name,
                'image': image,
            })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.get(
            author = self.writer,
            name = name,
            text = text,
            tag = tag,
        ).image.path.startswith(settings.MEDIA_ROOT + r'\media\articles\images\test1'))


    def test_post_bio_form(self):
        bio = 'bio'
        age = 54

        response = self.client.post(reverse('blog:my_page'), {
            'bio_form': ['Submit'],
            'bio': bio,
            'age': age,
        })

        writer = Writer.objects.get(name='writer0')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(writer.age, age)
        self.assertEqual(writer.bio, bio)


    def test_post_image_form(self):
        with open(settings.MEDIA_ROOT + r'\media\test\images\test2.jpg', 'rb') as image:
            image = SimpleUploadedFile('test2.jpg', image.read(), content_type='image/jpeg')

        response = self.client.post(reverse('blog:my_page'), {
            'image_form': ['Submit'],
            'image': image,
        })

        writer = Writer.objects.get(name=self.user.username)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(writer.image.path.startswith(settings.MEDIA_ROOT + r'\media\writers\images\test2'))

@unittest.skip('done')
class MyArticleViewTests(TestCase):

    def setUp(self):
        self.tag = create_tag('No tag')
        self.user = create_user('writer0', 'writer0')
        self.writer = create_writer('writer0', 0)
        self.client.login(username='writer0', password='writer0')
        with open(settings.MEDIA_ROOT + r'\media\test\images\test0.jpg', 'rb') as image:
            image = SimpleUploadedFile('test0.jpg', image.read(), content_type='image/jpeg')
            self.article = self.writer.article_set.create(
                name = 'article1',
                text = 'article1 text',
                tag = self.tag,
                image = image,
                pub_date = timezone.now(),
                last_edit = timezone.now()
            )


    def test_get_status_200(self):
        response = self.client.get(reverse('blog:my_article', args=(self.article.name, )))
        self.assertEqual(response.status_code, 200)


@unittest.skip('done')
class EditViewTests(TestCase):

    def setUp(self):
        self.tag = create_tag('No tag')
        self.user = create_user('writer0', 'writer0')
        self.writer = create_writer('writer0', 0)
        self.client.login(username='writer0', password='writer0')
        with open(settings.MEDIA_ROOT + r'\media\test\images\test0.jpg', 'rb') as image:
            image = SimpleUploadedFile('test0.jpg', image.read(), content_type='image/jpeg')
            self.article = self.writer.article_set.create(
                name = 'article1',
                text = 'article1 text',
                tag = self.tag,
                image = image,
                pub_date = timezone.now(),
                last_edit = timezone.now()
            )


    def test_get_response_200(self):
        response = self.client.get(reverse('blog:edit', args=(self.article.name, )))
        self.assertEqual(response.status_code, 200)


    def test_post_edits_article_without_image(self):
        new_name = 'New article name'
        new_text = 'New article text'
        new_tag = create_tag('Design')

        response = self.client.post(
            reverse('blog:edit', args=(self.article.name, )),{
                'name': new_name,
                'text': new_text,
                'tag': new_tag
            })

        self.assertTrue(Article.objects.get(
            author = self.writer,
            name = new_name,
            text = new_text,
            tag = new_tag,
        ).image.path.startswith(settings.MEDIA_ROOT + r'\media\articles\images\test0'))


        def test_post_edits_article_with_image(self):
            new_name = 'New article name'
            new_text = 'New article text'
            new_tag = create_tag('Design')
            with open(settings.MEDIA_ROOT + r'\media\test\images\test1.jpg', 'rb') as image:
                new_image = SimpleUploadedFile('test1.jpg', image.read(), content_type='image/jpeg')

            response = self.client.post(
                reverse('blog:edit', args=(self.article.name, )),{
                    'name': new_name,
                    'text': new_text,
                    'tag': new_tag,
                    'image': new_image
                })

            self.assertEqual(Article.objects.get(
                author = self.writer,
                name = new_name,
                text = new_text,
                tag = new_tag,
            ).image.path.startswith(settings.MEDIA_ROOT + r'\media\articles\images\test1'))


@unittest.skip('done')
class DeleteViewTests(TestCase):

    def setUp(self):
        self.tag = create_tag('No tag')
        self.user = create_user('writer0', 'writer0')
        self.writer = create_writer('writer0', 0)
        self.client.login(username='writer0', password='writer0')
        with open(settings.MEDIA_ROOT + r'\media\test\images\test0.jpg', 'rb') as image:
            image = SimpleUploadedFile('test0.jpg', image.read(), content_type='image/jpeg')
            self.article = self.writer.article_set.create(
                name = 'article1',
                text = 'article1 text',
                tag = self.tag,
                image = image,
                pub_date = timezone.now(),
                last_edit = timezone.now()
            )


    def test_get_deletes_article(self):
        response = self.client.get(reverse('blog:delete', args=(self.article.name, )))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Article.objects.filter(author=self.writer, name=self.article.name).exists())


    def test_get_dont_deletes_article_if_unauthenticated(self):
        client = Client()
        response = client.get(reverse('blog:delete', args=(self.article.name, )))
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Article.objects.filter(author=self.writer, name=self.article.name).exists())

@unittest.skip('done')
class LogInViewTests(TestCase):

    def test_get_response_200(self):
        response = self.client.get(reverse('blog:login'))
        self.assertEqual(response.status_code, 200)


    def test_if_login_post_logs_user_in(self):
        name = 'username'
        password = 'password'

        user = User.objects.create_user(
            username = name,
            password = password
        )

        response = self.client.post(reverse('blog:login'), {'username': name, 'password': password})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.is_authenticated)

@unittest.skip('done')
class SingUpViewTests(TestCase):

    def test_get_response_200(self):
        response = self.client.get(reverse('blog:sign_up'))
        self.assertEqual(response.status_code, 200)


    def test_if_sign_up_post_creates_user_and_writer(self):
        name = 'username'
        password = 'password'

        response = self.client.post(reverse('blog:sign_up'), {'username': name, 'password': password})

        user = get_user(self.client)

        self.assertTrue(user.is_authenticated)
        self.assertTrue(User.objects.filter(username=name).exists())
        self.assertTrue(Writer.objects.filter(name=name).exists())

        self.assertEquals(response.status_code, 302)

@unittest.skip('done')
class LogOutViewTests(TestCase):

    def test_if_logout_post_logs_user_out(self):
        name = 'username'
        password = 'password'

        User.objects.create_user(
            username = name,
            password = password
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.client.login(username = name, password = password)

        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse('blog:logout'))

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.assertEquals(response.status_code, 302)


@unittest.skip('done')
class AuthorsViewTestCase(TestCase):

    def test_status_200(self):
        response = self.client.get(reverse('blog:authors'))
        self.assertEqual(response.status_code, 200)

        for i in range(20):
            writer_name = 'writer' + str(i)
            create_writer(writer_name, i)
            response = self.client.get(reverse('blog:authors'))
            self.assertEqual(response.status_code, 200)


@unittest.skip('done')
class TagsViewTestCase(TestCase):

    def test_status_200(self):
        response = self.client.get(reverse('blog:authors'))
        self.assertEqual(response.status_code, 200)

        for i in range(20):
            tag_name = 'tag' + str(i)
            create_tag(tag_name)
            response = self.client.get(reverse('blog:authors'))
            self.assertEqual(response.status_code, 200)


@unittest.skip('done')
class TagViewTestCase(TestCase):

    def test_status_200(self):
        tag = create_tag('tag')
        response = self.client.get(reverse('blog:tag', args=(tag.name, )))
        self.assertEqual(response.status_code, 200)
