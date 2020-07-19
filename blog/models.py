import os
from PIL import Image

from django.core.files.storage import default_storage
from django.db.models import *
from django.conf import settings


def resize_image(path, square=False):
    image = Image.open(path)
    image.thumbnail((1500, 1500))

    if square:
        width_to_cut = abs(image.width - image.height) // 2
        if image.width > image.height:
            upper, lower = 0, image.height
            left, right = width_to_cut, image.width - width_to_cut
        elif image.height > image.width:
            left, right = 0, image.width
            upper, lower = width_to_cut, image.height - width_to_cut
        else:
            left, upper, right, lower = 0, 0, image.width, image.height

        image = image.crop((left, upper, right, lower))
    image.save(path)

    return Image.open(path)


def upload(instanse, path, file, square=False):
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
    with open(path, 'wb+') as dest:
        for c in file.chunks():
            dest.write(c)
    resize_image(path, square)
    instanse.image = path
    instanse.save()
    return path


def delete(instanse):
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
    image = ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, r'articles\images'), null=True)
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
        filename = os.path.join(os.path.join(settings.MEDIA_ROOT, r'\articles\images'), name)

        # upload
        return upload(self, filename, file)


    def delete_image(self):
        delete(self)


class Writer(Model):
    name = CharField(max_length=50)
    bio = CharField(max_length=1000, default='')
    age = IntegerField()
    image = ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, r'writers\images'), default=os.path.join(settings.MEDIA_ROOT, r'writers\images\default.jpg'), null=True)


    def __str__(self):
        return self.name


    def upload_image(self, file):
        # delete old
        self.delete_image()

        # get filename
        name = self.name + os.path.splitext(os.path.basename(file.name))[1]
        filename = os.path.join(os.path.join(settings.MEDIA_ROOT, r'writers\images'), name)

        # upload
        return upload(self, filename, file, square=True)


    def delete_image(self):
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
    image = ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, r'tags\images'), default=(settings.MEDIA_ROOT, r'tags\images\black.jpg'), null=True)


    def __str__(self):
        return self.name
