import unittest
from PIL import Image

from django.test import TestCase
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from blog.models import *


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


def create_article(writer, name, text, image=None, tag=None):
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


class ArticleModelTestCase(TestCase):

    def setUp(self):
        self.user = create_user('test_writer', 'test_writer')
        self.writer = create_writer('test_writer', 0)
        self.tag = create_tag('test_tag')
        with open(settings.MEDIA_ROOT + r'\test\images\test2.jpg', 'rb') as file:
            image = SimpleUploadedFile('test_writer_test_article.jpg', file.read(), content_type='image/jpg')
        self.article = create_article(self.writer, 'test_article', 'test_article text', image, self.tag)


    def tearDown(self):
        for name in default_storage.listdir('articles/images')[1]:
            if name.startswith('test_writer_test_article'):
                default_storage.delete('articles/images/' + name)

        for name in default_storage.listdir('writers/images')[1]:
            if name.startswith('test_writer'):
                default_storage.delete('writers/images/' + name)


    def test_upload_image(self):
        for i in range(3):
            with open(settings.MEDIA_ROOT + r'\test\images\test' + str(i) + '.jpg', 'rb') as file:
                image = SimpleUploadedFile('test' + str(i) + '.jpg', file.read(), content_type='image/jpg')
            self.article.upload_image(image)
            image = Image.open(os.path.join(settings.MEDIA_ROOT, 'articles/images/test_writer_test_article.jpg'))
            self.assertTrue(image.width <= 1500 and image.height <= 1500)
            self.assertIs(default_storage.listdir('articles/images')[1].count('test_writer_test_article.jpg'), 1)


    def test_delete_image(self):
        self.assertIs(default_storage.listdir('articles/images')[1].count('test_writer_test_article.jpg'), 1)
        self.article.delete_image()
        self.assertIs(default_storage.listdir('articles/images')[1].count('test_writer_test_article.jpg'), 0)
        self.assertIs(self.article.image.name, None)


class WriterModelTestCase(TestCase):

    def setUp(self):
        self.user = create_user('test_writer', 'test_writer')
        with open(settings.MEDIA_ROOT + r'\test\images\test1.jpg', 'rb') as file:
            image = SimpleUploadedFile('test_writer.jpg', file.read(), content_type='image/jpg')
        self.writer = create_writer('test_writer', 0, image)


    def tearDown(self):
        for name in default_storage.listdir('articles/images')[1]:
            if name.startswith('test_writer_test_article'):
                default_storage.delete('articles/images/' + name)

        for name in default_storage.listdir('writers/images')[1]:
            if name.startswith('test_writer'):
                default_storage.delete('writers/images/' + name)


    def test_upload_image(self):
        for i in range(3):
            with open(os.path.join(settings.MEDIA_ROOT, r'test\images\test' + str(i) + '.jpg'), 'rb') as file:
                image = SimpleUploadedFile('test' + str(i) + '.jpg', file.read(), content_type='image/jpg')
            self.writer.upload_image(image)
            image = Image.open(os.path.join(settings.MEDIA_ROOT, 'writers/images/test_writer.jpg'))
            self.assertTrue(image.width <= 1500 and image.height <= 1500)
            self.assertTrue(abs(image.width - image.height) <= 1)
            self.assertIs(default_storage.listdir('writers/images')[1].count('test_writer.jpg'), 1)


    def test_delete_image(self):
        self.assertIs(default_storage.listdir('writers/images')[1].count('test_writer.jpg'), 1)
        self.writer.delete_image()
        self.assertIs(default_storage.listdir('writers/images')[1].count('test_writer.jpg'), 0)
        self.assertIs(self.writer.image.name, None)
