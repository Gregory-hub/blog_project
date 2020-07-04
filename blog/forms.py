from django import forms
from django.contrib.auth.models import User

from .models import *


def get_choices():
    tags = Tag.objects.all()
    choices = []
    for tag in tags:
        choices.append((tag, tag.name))
    print(choices)
    return choices


class AddForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'id': 'title', 'placeholder': 'Title', 'autocomplete': 'off'}), max_length=70)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'art', 'class': 'textareacl', 'placeholder': 'Text' ,'autocomplete': 'off'}))
    tag = forms.ChoiceField(widget=forms.RadioSelect(), choices=get_choices())
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'id': 'avatarfile'}))


class WriterImageForm(forms.ModelForm):
    class Meta:
        model = Writer
        fields = ('image', )
        widgets = {
            'image': forms.ClearableFileInput(attrs={'id': 'af', 'name': 'avatarfile'}),
        }


class WriterBioForm(forms.ModelForm):

    class Meta:
        model = Writer
        fields = ('bio', 'age')
        widgets = {
            'bio': forms.Textarea(attrs={'id': 'itext', 'class': 'textareacl', 'name': 'info', 'placeholder': 'Information about you'}),
            'age': forms.TextInput(attrs={'id': "iage", 'placeholder': "Your age"})
        }


class SignUpForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username', 'autocomplete': 'off'}), max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'password', 'autocomplete': 'off'}), max_length=50)


class LogInForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your username', 'autocomplete': 'off'}), max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Your password', 'autocomplete': 'off'}), max_length=50)


class EditForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'id': 'title', 'placeholder': 'Title', 'autocomplete': 'off'}), max_length=70)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'art', 'class': 'textareacl', 'placeholder': 'Text' ,'autocomplete': 'off'}))
    tag = forms.ChoiceField(widget=forms.RadioSelect(), choices=get_choices())
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'id': 'avatarfile', 'name': 'avatarfile'}), required=False)


class CommentForm(forms.Form):
    text = forms.CharField(max_length=1000, widget=forms.TextInput, label="Comment")
