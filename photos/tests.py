import json
import jwt
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from photos.models import Photo, PhotoAlbum, PhotoAlbumItem

class PhotoAlbumTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.token = jwt.encode({'user_id': self.user.id}, settings.SECRET_KEY, algorithm='HS256')
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def test_create_album(self):
        url = reverse('photo_album_create')
        data = {
            'title': 'My Vacation',
            'description': 'Photos from my trip'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json', **self.auth_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PhotoAlbum.objects.count(), 1)
        album = PhotoAlbum.objects.first()
        self.assertEqual(album.title, 'My Vacation')
        self.assertEqual(album.user, self.user)

    @patch('photos.views.get_gcs_native_client')
    def test_upload_photo_to_album(self, mock_gcs_client):
        # Setup mock
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_gcs_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Create album
        album = PhotoAlbum.objects.create(title='Test Album', user=self.user)
        
        url = reverse('photo_album_upload', kwargs={'photo_album_id': album.id})
        photo_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        
        response = self.client.post(url, {'file': photo_file}, **self.auth_headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Photo.objects.count(), 1)
        self.assertEqual(PhotoAlbumItem.objects.count(), 1)
        
        item = PhotoAlbumItem.objects.first()
        self.assertEqual(item.photo_album, album)
        self.assertEqual(item.photo.user, self.user)
        self.assertTrue(item.photo.gcs_key.startswith('photo/'))

    def test_add_existing_photo_to_album(self):
        album = PhotoAlbum.objects.create(title='Test Album', user=self.user)
        photo = Photo.objects.create(filename='existing.jpg', user=self.user)
        
        url = reverse('photo_album_add_photo', kwargs={'photo_album_id': album.id})
        data = {'photo_id': photo.id}
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json', **self.auth_headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PhotoAlbumItem.objects.count(), 1)
        self.assertEqual(PhotoAlbumItem.objects.first().photo, photo)

    def test_album_detail(self):
        album = PhotoAlbum.objects.create(title='Test Album', user=self.user, friendly_token='testtoken')
        photo = Photo.objects.create(filename='test.jpg', gcs_key='photo/test.jpg', user=self.user)
        PhotoAlbumItem.objects.create(photo_album=album, photo=photo, ordering=1)
        
        url = reverse('photo_album_detail', kwargs={'friendly_token': 'testtoken'})
        response = self.client.get(url, **self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['album']['title'], 'Test Album')
        self.assertEqual(len(data['photos']), 1)
        self.assertEqual(data['photos'][0]['id'], photo.id)

    def test_set_ordering_bugfix(self):
        album = PhotoAlbum.objects.create(title='Test Album', user=self.user)
        photo = Photo.objects.create(filename='test.jpg', user=self.user)
        item = PhotoAlbumItem.objects.create(photo_album=album, photo=photo, ordering=1)
        
        success = album.set_ordering(photo, 5)
        self.assertTrue(success)
        item.refresh_from_db()
        self.assertEqual(item.ordering, 5)
