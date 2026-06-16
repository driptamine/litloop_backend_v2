import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User

class GoogleOAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.google_token_url = reverse('google_login_api') # I need to check the name in urls.py

    @patch('auth_cookie.apis.google_get_access_token')
    @patch('auth_cookie.apis.google_get_user_info')
    def test_google_login_success(self, mock_get_user_info, mock_get_access_token):
        # Mock access token response
        mock_get_access_token.return_value = {'access_token': 'fake_access_token'}
        
        # Mock user info response
        mock_get_user_info.return_value = {
            'email': 'googleuser@example.com',
            'picture': 'http://example.com/photo.jpg',
            'given_name': 'GoogleUser'
        }

        response = self.client.post(
            self.google_token_url,
            data=json.dumps({'code': 'valid_code'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['email'], 'googleuser@example.com')
        self.assertEqual(data['user']['username'], 'GoogleUser')
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='googleuser@example.com').exists())

    @patch('auth_cookie.apis.google_get_access_token')
    @patch('auth_cookie.apis.google_get_user_info')
    def test_google_login_existing_user(self, mock_get_user_info, mock_get_access_token):
        # Create existing user
        User.objects.create(email='existing@example.com', username='existing')
        
        # Mock responses
        mock_get_access_token.return_value = {'access_token': 'fake_token'}
        mock_get_user_info.return_value = {
            'email': 'existing@example.com',
            'picture': 'http://example.com/photo.jpg',
            'given_name': 'NewName' # Should probably keep the old username or update it depending on logic
        }

        response = self.client.post(
            self.google_token_url,
            data=json.dumps({'code': 'valid_code'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['created'])
        self.assertEqual(data['user']['email'], 'existing@example.com')
        
        # Verify no new user was created
        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)

    @patch('auth_cookie.apis.google_get_access_token')
    @patch('auth_cookie.apis.google_get_user_info')
    def test_google_login_username_collision(self, mock_get_user_info, mock_get_access_token):
        # Create user with a username that will collide
        User.objects.create(email='other@example.com', username='John')
        
        # Mock responses
        mock_get_access_token.return_value = {'access_token': 'fake_token'}
        mock_get_user_info.return_value = {
            'email': 'newuser@example.com',
            'picture': 'http://example.com/photo.jpg',
            'given_name': 'John' # Collides with existing 'John'
        }

        response = self.client.post(
            self.google_token_url,
            data=json.dumps({'code': 'valid_code'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['created'])
        self.assertEqual(data['user']['email'], 'newuser@example.com')
        # Username should be changed (appended with random string)
        self.assertNotEqual(data['user']['username'], 'John')
        self.assertTrue(data['user']['username'].startswith('John_'))
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    @patch('auth_cookie.apis.google_get_access_token')
    def test_google_login_invalid_code(self, mock_get_access_token):
        # Mock access token failure
        mock_get_access_token.side_effect = Exception("Failed to obtain access token")

        response = self.client.post(
            self.google_token_url,
            data=json.dumps({'code': 'invalid_code'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_google_login_missing_code(self):
        response = self.client.post(
            self.google_token_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        # DRF will return errors in field names
        self.assertIn('code', response.json())
