# tasks.py

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
# from views.models import View
from posts.models import Post, PostView, PostLike, PostImpression



@shared_task
def process_post_like(user_id, post_id):
    user = User.objects.get(id=user_id)
    post = Post.objects.get(id=post_id)

    like, created = PostLike.objects.get_or_create(user=user, post=post)

    if not created:
        like.delete()  # Toggle like (if already liked, remove it)

    return {'liked': created, 'post_id': post_id}

    
@shared_task
def process_view(user_id, post_id):
    try:
        user = User.objects.get(pk=user_id)
        post = Post.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return

    # Check if the user has already viewed the post
    if PostView.objects.filter(user=user, post=post).exists():
        return

    # Create a new View object
    view = PostView(user=user, post=post)
    view.save()

    # Update the like count of the post
    # post.views = View.objects.filter(post=post).count()
    # post.save()


@shared_task
def record_impressions_batch(post_ids, user_id):
    from django.db import models
    recorded = 0
    for post_id in post_ids:
        try:
            post = Post.objects.get(id=post_id)
            PostImpression.objects.create(post=post, user_id=user_id)
            Post.objects.filter(id=post_id).update(impressions_count=models.F('impressions_count') + 1)
            recorded += 1
        except Post.DoesNotExist:
            continue
    return {'recorded': recorded}
