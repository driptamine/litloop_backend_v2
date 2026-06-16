from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from .services import StorageService

class PresignedUrlSerializer(serializers.Serializer):
    file_path = serializers.CharField()
    file_type = serializers.CharField()
    provider = serializers.ChoiceField(choices=['s3', 'gcs'], required=False)

class PresignedUrlApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PresignedUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = StorageService.get_presigned_url(
            file_path=serializer.validated_data['file_path'],
            file_type=serializer.validated_data['file_type'],
            provider=serializer.validated_data.get('provider')
        )

        return Response(data, status=status.HTTP_200_OK)
