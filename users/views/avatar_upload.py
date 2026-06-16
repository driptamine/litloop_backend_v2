import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from rest_framework.permissions import IsAuthenticated
from uploader.gcs import gcs_upload_file
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AvatarUploadView(APIView):
    """
    API endpoint to upload a user avatar to GCS.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'avatar',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='Avatar image file'
            )
        ],
        responses={200: openapi.Response('Success', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'avatar': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ))}
    )
    def post(self, request, *args, **kwargs):
        if 'avatar' not in request.FILES:
            return Response({'error': 'No file provided in "avatar" field.'}, status=status.HTTP_400_BAD_REQUEST)

        avatar_file = request.FILES['avatar']
        
        # Validation for image files
        if not avatar_file.content_type.startswith('image/'):
            return Response({'error': 'File must be an image.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a unique filename to avoid collisions
        ext = os.path.splitext(avatar_file.name)[1]
        if not ext:
            # Fallback for some browsers/files
            ext = '.jpg' if avatar_file.content_type == 'image/jpeg' else '.png'
        
        filename = f"avatars/{request.user.id}_{uuid.uuid4()}{ext}"

        try:
            # Upload to GCS
            public_url = gcs_upload_file(avatar_file, filename, content_type=avatar_file.content_type)
            
            # Update user record
            user = request.user
            user.avatar = public_url
            user.save(update_fields=['avatar'])

            return Response({
                'message': 'Avatar uploaded successfully',
                'avatar': public_url
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Failed to upload to GCS: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

upload_avatar_view = AvatarUploadView.as_view()
