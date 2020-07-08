from django.db.models import *


class Article(Model):
    author = ForeignKey('Writer', on_delete=CASCADE)
    name = CharField(max_length=70)
    text = CharField(max_length=100000)
    image = ImageField(upload_to='media/articles/images/')
    tag = ForeignKey('Tag', on_delete=CASCADE, null=True)
    pub_date = DateTimeField()
    last_edit = DateTimeField()

    def __str__(self):
        return self.name


class Writer(Model):
    name = CharField(max_length=50)
    bio = CharField(max_length=1000, default='')
    age = IntegerField()
    image = ImageField(upload_to='media/writers/images/', default='media/writers/images/default.jpg')

    def __str__(self):
        return self.name


class Comment(Model):
    article = ForeignKey('Article', on_delete=CASCADE)
    author = ForeignKey('Writer', on_delete=CASCADE)
    text = CharField(max_length=1000)
    comment_date = DateTimeField()

    def __str__(self):
        return self.text


class Tag(Model):
    name = CharField(max_length=70)
    image = ImageField(upload_to='media/tags/images/', default='media/tags/images/Metallica_-_Metallica_cover.jpg')

    def __str__(self):
        return self.name
