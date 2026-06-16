import json
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from rest_framework.exceptions import AuthenticationFailed
from users.services import user_create, user_get_or_create
from users.serializers import RegisterSerializer, LoginSerializer

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.signin_url = reverse('signin')
        self.user_data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpassword123',
            'avatar': 'http://example.com/avatar.png'
        }

    def test_signup_success(self):
        response = self.client.post(
            self.signup_url,
            data=json.dumps(self.user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.json())
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_signup_without_username(self):
        data = {
            'email': 'no_username@example.com',
            'password': 'password123'
        }
        response = self.client.post(
            self.signup_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.json())
        user = User.objects.get(email='no_username@example.com')
        # Username should be generated from email prefix
        self.assertEqual(user.username, 'no_username')

    def test_signup_missing_fields(self):
        incomplete_data = {'email': 'testuser@example.com'}
        response = self.client.post(
            self.signup_url,
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        # DRF returns field-level errors. Since only password is missing (username is optional),
        # only password error should be present.
        # Wait, the non-drf view returns {'error': 'Email and password are required'}
        # Let's check the error message.
        self.assertEqual(response.json()['error'], 'Email and password are required')

    def test_signup_duplicate_username(self):
        User.objects.create_user(**self.user_data)
        duplicate_username_data = self.user_data.copy()
        duplicate_username_data['email'] = 'different_email@example.com'
        
        response = self.client.post(
            self.signup_url,
            data=json.dumps(duplicate_username_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        # The username should have been changed because of collision handling
        self.assertNotEqual(response.json()['user']['username'], self.user_data['username'])
        self.assertTrue(response.json()['user']['username'].startswith(self.user_data['username']))

    def test_signin_success_with_email(self):
        User.objects.create_user(**self.user_data)
        signin_data = {
            'email_or_username': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_signin_success_with_username(self):
        User.objects.create_user(**self.user_data)
        signin_data = {
            'email_or_username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_signin_invalid_credentials(self):
        User.objects.create_user(**self.user_data)
        signin_data = {
            'email_or_username': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'Invalid credentials')

    def test_signin_non_existent_user(self):
        signin_data = {
            'email_or_username': 'nonexistent',
            'password': 'somepassword'
        }
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'Invalid credentials')

    def test_signup_empty_json(self):
        response = self.client.post(
            self.signup_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Email and password are required')

    def test_signin_empty_json(self):
        response = self.client.post(
            self.signin_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Email/username and password are required')

    def test_user_me_unauthenticated(self):
        url = reverse('user_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'Not authenticated')

    def test_user_me_authenticated_session(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_login(user)
        url = reverse('user_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], user.email)

    def test_user_me_authenticated_jwt(self):
        user = User.objects.create_user(**self.user_data)
        from users.jwt_auth import generate_jwt
        token = generate_jwt(user)
        url = reverse('user_me')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], user.email)


class UserServiceTests(TestCase):
    def test_user_create_success(self):
        user = user_create(
            email='service@example.com', 
            username='serviceuser', 
            password='password123',
            avatar='http://example.com/avatar.png'
        )
        self.assertEqual(user.email, 'service@example.com')
        self.assertTrue(user.check_password('password123'))

    def test_user_get_or_create(self):
        # First time - create
        user, created = user_get_or_create(
            email='getcreate@example.com', 
            username='getcreate',
            avatar='http://example.com/avatar.png'
        )
        self.assertTrue(created)
        self.assertEqual(user.email, 'getcreate@example.com')

        # Second time - get
        user2, created2 = user_get_or_create(email='getcreate@example.com')
        self.assertFalse(created2)
        self.assertEqual(user.id, user2.id)


class UserSerializerTests(TestCase):
    def test_register_serializer_valid(self):
        data = {
            'email': 'serializer@example.com',
            'username': 'serializeruser',
            'password': 'password123',
            'avatar': 'http://example.com/avatar.png'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'serializer@example.com')

    def test_register_serializer_invalid_username(self):
        data = {
            'email': 'serializer@example.com',
            'username': 'user!name',
            'password': 'password123',
            'avatar': 'http://example.com/avatar.png'
        }
        serializer = RegisterSerializer(data=data)
        # It should be valid and clean the username
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'username')

    def test_login_serializer_valid(self):
        user = User.objects.create_user(
            email='login@example.com', 
            username='loginuser', 
            password='password123',
            avatar='http://example.com/avatar.png'
        )
        # User needs to be verified for LoginSerializer to work
        user.is_verified = True
        user.save()

        data = {
            'email': 'login@example.com',
            'password': 'password123'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'login@example.com')
        self.assertIn('access_token', serializer.validated_data)

    def test_login_serializer_invalid_credentials(self):
        User.objects.create_user(
            email='login@example.com', 
            username='loginuser', 
            password='password123',
            avatar='http://example.com/avatar.png'
        )
        data = {
            'email': 'login@example.com',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=data)
        # LoginSerializer doesn't require avatar because it's read_only in LoginSerializer or just not part of validation
        # Wait, LoginSerializer Meta fields include 'avatar'.
        with self.assertRaises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)
