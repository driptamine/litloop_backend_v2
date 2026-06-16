from rest_framework import serializers
from users.models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
# from posts.serializers import PostsSerializer

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True
    )
    username = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'password',
            'avatar',
        ]

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username')

        if not username:
            # Use email prefix as username
            username = email.split('@')[0].replace('.', '_')
            
        # Handle username collision
        import random
        base_username = username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{random.randint(100, 999)}"
        
        if not username.isalnum():
            import re
            username = re.sub(r'[^a-zA-Z0-9]', '', username)
            
        attrs['username'] = username
            
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=555)

    class Meta:
        model  = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3,)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    avatar = serializers.CharField(max_length=400, read_only=True)
    # tokens = serializers.CharField(max_length=68, read_only=True)
    access_token = serializers.CharField(max_length=68, read_only=True)
    refresh_token = serializers.CharField(max_length=68, read_only=True)
    # tokens = serializers.JSONField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'avatar',
            'username',
            'access_token',
            'refresh_token'
        ]


    def validate(self, attrs):
        email = attrs.get('email', '')
        # username = attrs.get('username', '')
        password = attrs.get('password', '')
        # username_or_email = username or email

        # if User.objects.filter(username=username).exists:
        #     user = auth.authenticate(username=username, password=password)
        # else:
        #     user = auth.authenticate(email=username, password)

        user = auth.authenticate(email=email, password=password)
        # user = auth.authenticate(username=username_or_email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')


        return {
            'id': user.id,
            'email': user.email,
            'avatar': user.avatar,
            'username': user.username,
            'access_token': user.access_token,
            'refresh_token': user.refresh_token
        }


        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3,)
    # password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    # posts = PostsSerializer()

    class Meta:
        model = User
        fields = [
            'id',
            # 'uuid',
            'avatar',
            'username',
            'email',
            'created_at',
            'updated_at',
            # 'posts',
            # 'posts_count',
            # 'likes_count',
            # 'views_count',
        ]
    # class Meta:
    #     model = User
    #     fields = '__all__'
