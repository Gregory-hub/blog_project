from django.template import Library
from django.utils import timezone


register = Library()


@register.simple_tag
def get_datetime(pub_date):
    delta = timezone.now() - pub_date
    if delta.days > 0:
        if delta.days == 1:
            age = f'{delta.days} day ago'
        else:
            age = f'{delta.days} days ago'
    elif delta.seconds > 3599:
        hours = delta.seconds // 3600
        if hours == 1:
            age = f'{hours} hour ago'
        else:
            age = f'{hours} hours ago'
    else:
        minutes = delta.seconds // 60
        if minutes == 0:
            age = 'a moment ago'
        elif minutes == 1:
            age = f'{minutes} minute ago'
        else:
            age = f'{minutes} minutes ago'
    return age
