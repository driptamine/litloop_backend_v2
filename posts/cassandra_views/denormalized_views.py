from posts.models import PostLike

def like_post(user, post):
    obj, created = PostLike.objects.get_or_create(user=user, post=post)
    if created:
        post.likes_count = F('likes_count') + 1
        post.save(update_fields=['likes_count'])

def unlike_post(user, post):
    deleted, _ = PostLike.objects.filter(user=user, post=post).delete()
    if deleted:
        post.likes_count = F('likes_count') - 1
        post.save(update_fields=['likes_count'])
