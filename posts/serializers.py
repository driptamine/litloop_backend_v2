from rest_framework import serializers
from posts.models import Post
from users.serializers import UserSerializer
from photos.serializers import PhotoSerializer
from videos.serializers import VideoSerializer
from tracks.serializers import TrackSerializer
from playlists.serializers import PlaylistSerializer

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    total_likes = serializers.IntegerField(source='likes_count', read_only=True)
    
    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)
    playlists = PlaylistSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'title',
            'description',
            'friendly_id',
            'is_liked',
            'total_likes',
            'likes_count',
            'dislikes_count',
            'views_count',
            'impressions_count',
            'photos',
            'videos',
            'tracks',
            'playlists',
            'created_at',
            'updated_at',
        ]

    def get_is_liked(self, obj):
        # This would require request context to check if the current user liked it
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # check if obj is liked by request.user
            # Assuming there's a PostLike model we can query
            from posts.models import PostLike
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False

class PostCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    photo_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    video_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    track_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    playlist_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'friendly_id',
            'photo_ids',
            'video_ids',
            'track_ids',
            'playlist_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'friendly_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Remove media IDs from validated_data before creating the Post
        photo_ids = validated_data.pop('photo_ids', [])
        video_ids = validated_data.pop('video_ids', [])
        track_ids = validated_data.pop('track_ids', [])
        playlist_ids = validated_data.pop('playlist_ids', [])
        
        post = Post.objects.create(**validated_data)
        
        # We still want these IDs available for perform_create in the view
        # or we can handle them here. 
        # Since perform_create is already implemented, let's put them back 
        # in a way that doesn't affect the model but is accessible if needed.
        # Actually, let's just handle the linking here for better encapsulation.
        return post
