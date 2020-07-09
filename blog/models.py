import os
from PIL import Image

from django.core.files.storage import default_storage
from django.db.models import *
from django.conf import settings


def resize_image(path):
    image = Image.open(path)
    image.thumbnail((1500, 1500))
    image.save(path)

    return Image.open(path)


def upload(instanse, path, file):
    # upload
    with open(path, 'wb+') as dest:
        for c in file.chunks():
            dest.write(c)
    resize_image(path)
    instanse.image = path
    instanse.save()
    return path


def delete(instanse):
    print("delete")
    if instanse.image:
        path = instanse.image.path
        default_storage.delete(path)
        instanse.image = None
        instanse.save()
    else:
        path = None
    return path


class Article(Model):
    author = ForeignKey('Writer', on_delete=CASCADE)
    name = CharField(max_length=70)
    text = CharField(max_length=100000)
    image = ImageField(upload_to=r'media\articles\images', null=True)
    tag = ForeignKey('Tag', on_delete=CASCADE, null=True)
    pub_date = DateTimeField()
    last_edit = DateTimeField()


    def __str__(self):
        return self.name


    def upload_image(self, file):
        # delete old
        self.delete_image()

        # get filename
        name = self.author.name + '_' + self.name + os.path.splitext(os.path.basename(file.name))[1]
        filename = os.path.join(r'media\articles\images', name)

        # upload
        return upload(self, filename, file)


    def delete_image(self):
        delete(self)


class Writer(Model):
    name = CharField(max_length=50)
    bio = CharField(max_length=1000, default='')
    age = IntegerField()
    image = ImageField(upload_to=r'media\writers\images', default=r'media\writers\images\default.jpg', null=True)


    def __str__(self):
        return self.name


    def upload_image(self, file):
        # delete old
        self.delete_image()

        # get filename
        name = self.name + os.path.splitext(os.path.basename(file.name))[1]
        filename = os.path.join(r'media\writers\images', name)

        # upload
        return upload(self, filename, file)


    def delete_image(self):
        print("delete_image")
        delete(self)


class Comment(Model):
    article = ForeignKey('Article', on_delete=CASCADE)
    author = ForeignKey('Writer', on_delete=CASCADE)
    text = CharField(max_length=1000)
    comment_date = DateTimeField()


    def __str__(self):
        return self.text


class Tag(Model):
    name = CharField(max_length=70)
    image = ImageField(upload_to=r'media\tags\images', default=r'media\tags\images\Metallica_-_Metallica_cover.jpg', null=True)


    def __str__(self):
        return self.name
