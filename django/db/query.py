from datetime import datetime

from django.db.models import Q, Count, Avg
from pytz import UTC

from db.models import User, Blog, Topic


def create():
    u1 = User(first_name='u1', last_name='u1')
    u1.save()
    u2 = User(first_name='u2', last_name='u2')
    u2.save()
    u3 = User(first_name='u3', last_name='u3')
    u3.save()

    b1 = Blog(title='blog1', author=u1)
    b1.save()
    b2 = Blog(title='blog2', author=u1)
    b2.save()

    b1.subscribers.add(u1, u2)
    b1.save()
    b2.subscribers.add(u2)
    b2.save()

    topic1 = Topic(title='topic1', blog=b1, author=u1)
    topic1.save()
    topic2 = Topic(title='topic2_content', blog=b1, author=u3,
                   created=datetime(2017, 1, 1, tzinfo=UTC))
    topic2.save()

    topic1.likes.add(u1, u2, u3)
    topic1.save()


def edit_all():
    for user in User.objects.all():
        user.first_name = 'uu1'
        user.save()


def edit_u1_u2():
    for user in User.objects.filter(first_name__in=['u1', 'u2']):
        user.first_name = 'uu1'
        user.save()


def delete_u1():
    User.objects.get(first_name='u1').delete()


def unsubscribe_u2_from_blogs():
    User.objects.get(first_name='u2').subscriptions.clear()


def get_topic_created_grated():
    return Topic.objects.filter(created__gt=datetime(2018, 1, 1, tzinfo=UTC))


def get_topic_title_ended():
    return Topic.objects.filter(title__endswith='content')


def get_user_with_limit():
    return User.objects.order_by('-pk')[:2]


def get_topic_count():
    return Blog.objects.annotate(topic_count=Count('topic')).order_by(
        'topic_count')


def get_avg_topic_count():
    return Blog.objects.annotate(topic_count=Count('topic')).aggregate(
        Avg('topic_count'))['topic_count__avg']


def get_blog_that_have_more_than_one_topic():
    return Blog.objects.annotate(topic_count=Count('topic')).filter(
        topic_count__gt='1')


def get_topic_by_u1():
        return Topic.objects.filter(author__first_name='u1')


def get_user_that_dont_have_blog():
    return User.objects.filter(blog__isnull=True).order_by('pk')


def get_topic_that_like_all_users():
    return Topic.objects.filter(likes=(User.objects.all()))


def get_topic_that_dont_have_like():
    return Topic.objects.filter(likes__isnull=True)
