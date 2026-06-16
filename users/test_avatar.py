import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class AvatarUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('upload_avatar')
        self.user_data = {
            'email': 'avataruser@example.com',
            'username': 'avataruser',
            'password': 'password123'
        }
        self.user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    @patch('users.views.avatar_upload.gcs_upload_file')
    def test_upload_avatar_success(self, mock_upload):
        mock_url = 'https://storage.googleapis.com/bucket/avatars/test.png'
        mock_upload.return_value = mock_url
        
        avatar_file = SimpleUploadedFile("avatar.png", b"file_content", content_type="image/png")
        
        response = self.client.post(
            self.url,
            {'avatar': avatar_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['avatar'], mock_url)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, mock_url)
        mock_upload.assert_called_once()

    def test_upload_avatar_unauthenticated(self):
        self.client.credentials()  # Clear credentials
        avatar_file = SimpleUploadedFile("avatar.png", b"file_content", content_type="image/png")
        response = self.client.post(self.url, {'avatar': avatar_file}, format='multipart')
        self.assertEqual(response.status_code, 401)

    def test_upload_avatar_no_file(self):
        response = self.client.post(
            self.url,
            {},
            format='multipart'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'No file provided in "avatar" field.')

    def test_upload_avatar_invalid_method(self):
        response = self.client.get(
            self.url
        )
        self.assertEqual(response.status_code, 405)

    def test_upload_avatar_not_image(self):
        avatar_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        response = self.client.post(
            self.url,
            {'avatar': avatar_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'File must be an image.')
