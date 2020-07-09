import os

from django.core.files.storage import default_storage
from django.db.models import *


class Article(Model):
    author = ForeignKey('Writer', on_delete=CASCADE)
    name = CharField(max_length=70)
    text = CharField(max_length=100000)
    image = ImageField(upload_to='media/articles/images/', null=True)
    tag = ForeignKey('Tag', on_delete=CASCADE, null=True)
    pub_date = DateTimeField()
    last_edit = DateTimeField()


    def __str__(self):
        return self.name


    def upload_image(self, file):
        # delete
        if self.image:
            path = self.image.path
            default_storage.delete(path)

        # upload
        filename = default_storage.get_available_name(os.path.join('media/articles/images/', file.name))
        with open(filename, 'wb+') as dest:
            for c in file.chunks():
                dest.write(c)
        self.image = filename
        return filename


    def delete_image(self):
        if self.image:
            path = self.image.path
            default_storage.delete(path)
        return path


class Writer(Model):
    name = CharField(max_length=50)
    bio = CharField(max_length=1000, default='')
    age = IntegerField()
    image = ImageField(upload_to='media/writers/images/', default='media/writers/images/default.jpg', null=True)

    def __str__(self):
        return self.name


    def upload_image(self, file):
        # delete old image
        if self.image:
            path = self.image.path
            default_storage.delete(path)

        # upload
        filename = default_storage.get_available_name(os.path.join('media/articles/images/', file.name))
        with open(filename, 'wb+') as dest:
            for c in file.chunks():
                dest.write(c)
        self.image = filename
        return filename


    def delete_image(self):
        if self.image:
            path = self.image.path
            default_storage.delete(path)
        return path


class Comment(Model):
    article = ForeignKey('Article', on_delete=CASCADE)
    author = ForeignKey('Writer', on_delete=CASCADE)
    text = CharField(max_length=1000)
    comment_date = DateTimeField()

    def __str__(self):
        return self.text


class Tag(Model):
    name = CharField(max_length=70)
    image = ImageField(upload_to='media/tags/images/', default='media/tags/images/Metallica_-_Metallica_cover.jpg', null=True)

    def __str__(self):
        return self.name


    def upload_image(self, file):
        # delete
        if self.image:
            path = self.image.path
            default_storage.delete(path)

        # upload
        filename = default_storage.get_available_name(os.path.join('media/articles/images/', file.name))
        with open(filename, 'wb+') as dest:
            for c in file.chunks():
                dest.write(c)
        self.image = filename
        return filename


    def delete_image(self):
        if self.image:
            path = self.image.path
            default_storage.delete(path)
        return path
