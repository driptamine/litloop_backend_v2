from rest_framework import generics, permissions, status
from rest_framework.response import Response
from posts.models import Post, Photo, Video, Track, Playlist, PostPhoto, PostVideo, PostTrack, PostPlaylist
from posts.serializers import PostCreateSerializer, PostSerializer

class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the author to the current user
        post = serializer.save(author=self.request.user)
        
        # Optionally handle media IDs if provided in the request data
        photo_ids = serializer.validated_data.get('photo_ids', [])
        video_ids = serializer.validated_data.get('video_ids', [])
        track_ids = serializer.validated_data.get('track_ids', [])
        playlist_ids = serializer.validated_data.get('playlist_ids', [])

        for i, pid in enumerate(photo_ids):
            try:
                photo = Photo.objects.get(id=pid)
                PostPhoto.objects.get_or_create(post=post, photo=photo, defaults={'order': i+1})
            except Photo.DoesNotExist:
                continue

        for i, vid in enumerate(video_ids):
            try:
                video = Video.objects.get(id=vid)
                PostVideo.objects.get_or_create(post=post, video=video, defaults={'order': i+1})
            except Video.DoesNotExist:
                continue

        for i, tid in enumerate(track_ids):
            try:
                track = Track.objects.get(id=tid)
                PostTrack.objects.get_or_create(post=post, track=track, defaults={'order': i+1})
            except Track.DoesNotExist:
                continue

        for i, pid in enumerate(playlist_ids):
            try:
                playlist = Playlist.objects.get(id=pid)
                PostPlaylist.objects.get_or_create(post=post, playlist=playlist, defaults={'order': i+1})
            except Playlist.DoesNotExist:
                continue

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the full post data using PostSerializer
        full_serializer = PostSerializer(serializer.instance, context={'request': request})
        headers = self.get_success_headers(full_serializer.data)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
