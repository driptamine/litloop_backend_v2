class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.FileField(upload_to=user_directory_path, default="")

class Photo(models.Model):
    s3_key          = models.CharField(max_length=400, null=True)
    gcs_key         = models.CharField(max_length=400, null=True, blank=True)
    filename        = models.CharField(max_length=400, null=True)
    user            = models.ForeignKey("users.User", on_delete=models.CASCADE)

class Video(models.Model):
    s3_key          = models.CharField(max_length=400)
    gcs_key         = models.CharField(max_length=400, null=True, blank=True)
    filename        = models.CharField(max_length=400)
    user            = models.ForeignKey("users.User", on_delete=models.CASCADE)


class Post(models.Model):

    videos      = models.ManyToManyField(Video, through="PostVideo", blank=True)
    photos      = models.ManyToManyField(Photo, through="PostPhoto", blank=True)


    title       = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=100, blank=True)

    author      = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    caption     = models.CharField(max_length=50, blank=True)
    image       = models.FileField(upload_to=post_directory_path, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    likes       = models.ManyToManyField(User, through='PostLike', blank=True, related_name='post_likes')
    dislikes    = models.ManyToManyField(User, through='PostDislike', blank=True, related_name='post_dislikes')


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class PostDislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo = models.ForeignKey('photos.Photo', on_delete=models.CASCADE)
    order = models.IntegerField(default=1)

class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
