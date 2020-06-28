import unittest
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout, get_user
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import *


def create_writer(name):
    writer = Writer.objects.create(name=name)
    return writer


def create_article(writer, name, text, tag=None):
    article = writer.article_set.create(
        name=name,
        text=text,
        pub_date=timezone.now(),
        last_edit=timezone.now()
    )
    return article


def create_user(username, password):
    user = User.objects.create_user(username=username, password=password)
    Writer.objects.create(name=username)
    return user


@unittest.skip('')
class IndexViewTestCase(TestCase):

    def test_status_200(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)

@unittest.skip('')
class ArticleViewTestCase(TestCase):

    def test_status_200(self):
        writer = create_writer('writer1')
        article = create_article(writer, 'article1', 'article1 text')
        response = self.client.get(reverse('blog:article', args=(writer.name, article.name)))
        self.assertEqual(response.status_code, 200)


    def test_unexisting_writer(self):
        writer = create_writer('writer1')
        article = create_article(writer, 'article1', 'article1 text')
        response = self.client.get(reverse('blog:article', args=('random_name', article.name)))
        self.assertEqual(response.status_code, 404)


    def test_unexisting_article(self):
        writer = create_writer('writer1')
        response = self.client.get(reverse('blog:article', args=(writer.name, 'random_name')))
        self.assertEqual(response.status_code, 404)


    def test_comment_creation(self):
        name = 'username'
        password = 'password'
        text = 'comment text'

        writer = create_writer('writer1')
        article = create_article(writer, 'article1', 'article1 text')

        self.assertTrue(Writer.objects.filter(name='writer1').exists())

        create_user(name, password)
        self.client.login(username=name, password=password)

        response = self.client.post(
            reverse('blog:article', args=(writer.name, article.name)),
            {'text': text},
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Comment.objects.filter(article=article, text=text).exists())

@unittest.skip('')
class WriterViewTests(TestCase):

    def test_status_200(self):
        writer = create_writer('writer1')
        response = self.client.get(reverse('blog:writer', args=(writer.name, )))
        self.assertEqual(response.status_code, 200)

@unittest.skip('')
class MyPageViewTests(TestCase):

    def setUp(self):
        self.name = 'name'
        self.password = 'password'
        self.user = create_user(self.name, self.password)
        self.client.login(username=self.name, password=self.password)


    def test_get_status_200(self):
        response = self.client.get(reverse('blog:my_page'))
        self.assertEqual(response.status_code, 200)


    def test_if_no_articles(self):
        response = self.client.get(reverse('blog:my_page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'No articles')


    def test_if_5_articles(self):
        writer = Writer.objects.get(name=self.user.username)
        for i in range(5):
            writer.article_set.create(
                name = 'article' + str(i),
                text = 'article' + str(i) + ' text',
                pub_date = timezone.now(),
                last_edit = timezone.now()
            )
        response = self.client.get(reverse('blog:my_page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['articles'].count(), 5)


    def test_post_adds_image_to_writer(self):

        with open(r'C:\Gry\Files\Django\blog_project\media\images_for_tests\Без названия (2).jpg', 'rb') as file:
            image = SimpleUploadedFile('image.jpg', file.read(), content_type='image/jpg')

        response = self.client.post(reverse('blog:my_page'), {'image': image})

        writer = Writer.objects.get(name=self.user.username)

        self.assertEquals(response.status_code, 302)
        self.assertTrue(writer.image.name.startswith('writers/images/image'))
        self.assertTrue(writer.image.name.endswith('.jpg'))

@unittest.skip('')
class MyArticleViewTests(TestCase):

    def setUp(self):
        self.name = 'name'
        self.password = 'password'
        self.user = create_user(self.name, self.password)
        self.writer = Writer.objects.get(name=self.user.username)
        self.article = self.writer.article_set.create(
            name = 'article1',
            text = 'article1 text',
            pub_date = timezone.now(),
            last_edit = timezone.now()
        )
        self.client.login(username=self.name, password=self.password)


    def test_get_status_200(self):
        response = self.client.get(reverse('blog:my_article', args=(self.article.name, )))
        self.assertEqual(response.status_code, 200)


    def test_post_delete_deletes_article(self):
        name = self.article.name
        response = self.client.post(reverse('blog:my_article', args=(self.article.name, )), {'value': 'delete'})

        self.assertFalse(Article.objects.filter(name=name).exists())
        self.assertEqual(response.status_code, 302)


    def test_post_edit_redirects_to_edit_page(self):
        name = self.article.name
        response = self.client.post(reverse('blog:my_article', args=(self.article.name, )), {'value': 'edit'}, follow=True)

        self.assertTrue(('/blog/my_page/article1/edit/', 302) in response.redirect_chain)


class AddViewTests(TestCase):

    def setUp(self):
        self.user = create_user('username', 'password')
        self.client.login(username='username', password='password')
        self.tag = Tag.objects.create(name='test')


    def test_get_response_200(self):
        response = self.client.get(reverse('blog:add'))
        self.assertEquals(response.status_code, 200)


    # def test_post_adds_article(self):
    #     name = 'new name'
    #     text = 'new text'
    #
    #     response = self.client.post(reverse('blog:add'), {'name': name, 'text': text, 'tag': self.tag.name})
    #
    #     if response.context:
    #         print(response.context['message'])
    #
    #     self.assertTrue(Article.objects.filter(name=name, text=text).exists())


    # def test_post_unique_names(self):
    #
    #     tag = Tag.objects.create(name='tag')
    #
    #     name1 = 'name1'
    #     text1 = 'text1'
    #     response = self.client.post(reverse('blog:add'), {'name': name1, 'text': text1, 'tag': tag.name})
    #
    #     name2 = 'name1'
    #     text2 = 'text2'
    #     response = self.client.post(reverse('blog:add'), {'name': name2, 'text': text2, 'tag': tag.name})
    #
    #     self.assertEquals(response.status_code, 200)
    #     self.assertEquals(response.context['message'], 'This name is not available')

@unittest.skip('')
class EditViewTests(TestCase):

    def setUp(self):
        self.name = 'name'
        self.password = 'password'
        self.user = create_user(self.name, self.password)
        self.writer = Writer.objects.get(name=self.user.username)
        self.article = self.writer.article_set.create(
            name = 'article1',
            text = 'article1 text',
            pub_date = timezone.now(),
            last_edit = timezone.now()
        )
        self.client.login(username=self.name, password=self.password)


    def test_get_response_200(self):
        response = self.client.get(reverse('blog:edit', args=(self.article.name, )))
        self.assertEqual(response.status_code, 200)


    def test_post_edits_article(self):
        old_name = self.article.name
        old_text = self.article.text

        new_name = 'new article1 name'
        new_text = 'new article1 text'

        response = self.client.post(
            reverse('blog:edit', args=(self.article.name, )),
            {'name': new_name, 'text': new_text}
        )

        article = Article.objects.get(id=1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.name, new_name)
        self.assertEqual(article.text, new_text)
        self.assertTrue(timezone.now() - article.last_edit < timedelta(seconds=3))


    def test_post_unique_names(self):

        article2 = self.writer.article_set.create(
            name = 'article2',
            text = 'article2 text',
            pub_date = timezone.now(),
            last_edit = timezone.now()
        )

        response = self.client.post(
            reverse('blog:edit', args=(article2.name, )),
            {'name': 'article1', 'text': 'new article2 text'}
        )

        article = Article.objects.get(id=2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'This name is not available')
        self.assertEqual(article.name, 'article2')
        self.assertEqual(article.text, 'article2 text')


        create_user('writer2', 'password')
        writer2 = Writer.objects.get(name='writer2')
        article3 = writer2.article_set.create(
            name = 'article3',
            text = 'article3 text',
            pub_date = timezone.now(),
            last_edit = timezone.now()
        )

        self.client.login(username='writer2', password='password')
        response = self.client.post(
            reverse('blog:edit', args=(article3.name, )),
            {'name': 'article1', 'text': 'new article3 text'}
        )

        article = Article.objects.get(id=3)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.name, 'article1')
        self.assertEqual(article.text, 'new article3 text')


    def test_post_if_text_field_is_empty(self):

        old_text = self.article.text

        response = self.client.post(
            reverse('blog:edit', args=(self.article.name, )),
            {'name': 'new name', 'text': ''}
        )

        article = Article.objects.get(id=1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.name, 'new name')
        self.assertEqual(article.text, old_text)


    def test_post_if_name_field_is_empty(self):

        old_name = self.article.name

        response = self.client.post(
            reverse('blog:edit', args=(self.article.name, )),
            {'name': '', 'text': 'new text'}
        )

        article = Article.objects.get(id=1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.name, old_name)
        self.assertEqual(article.text, 'new text')

@unittest.skip('')
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

@unittest.skip('')
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

@unittest.skip('')
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
