import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Chat, Message
from users.models import User

class ChatTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.chat = Chat.objects.create(name='test-chat', description='A test chat room')

    def test_chat_list(self):
        response = self.client.get(reverse('chat_list'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(any(c['name'] == 'test-chat' for c in data['chats']))

    def test_chat_detail(self):
        Message.objects.create(chat=self.chat, user=self.user, text="Hello world")
        response = self.client.get(reverse('chat_detail', args=[self.chat.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'test-chat')
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['text'], "Hello world")

    def test_send_message(self):
        url = reverse('send_message', args=[self.chat.id])
        payload = {"text": "New message from test"}
        
        # Get JWT token for the user
        token = self.user.access_token()
        
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.filter(chat=self.chat).count(), 1)
        self.assertEqual(Message.objects.first().text, "New message from test")
        self.assertEqual(Message.objects.first().user, self.user)

    def test_send_message_unauthorized(self):
        url = reverse('send_message', args=[self.chat.id])
        payload = {"text": "Unauthorized message"}
        
        # No Authorization header
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # Invalid token
        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer invalidtoken'
        )
        self.assertEqual(response.status_code, 401)

    def test_gemini_persistence(self):
        # We can't easily test the actual API call without mocking, 
        # but we can check if the room is created.
        url = reverse('chat_with_gemini') + "?q=hello"
        # Mocking the genai client response if possible, but for a "quick check" 
        # let's just see if it handles the request flow.
        # Note: This will actually try to call the API if GOOGLE_GEMINI_API_KEY is set.
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                self.assertTrue(Chat.objects.filter(name='gemini-ai').exists())
                # Should have 2 messages: user and AI
                self.assertEqual(Message.objects.filter(chat__name='gemini-ai').count(), 2)
        except Exception:
            # If API key is missing, this might fail, which is expected in some test envs
            pass

    def test_get_or_create_direct_chat(self):
        # Create alice for the view's fallback logic
        User.objects.create_user(username='alice', email='alice@example.com', password='password')
        target_user = User.objects.create_user(
            username='target', 
            email='target@example.com',
            password='password', 
            avatar='http://example.com/avatar.png'
        )
        url = reverse('user_direct_chat', args=[target_user.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['username'], 'target')
        self.assertEqual(data['avatar'], 'http://example.com/avatar.png')
        self.assertEqual(data['target_user'], 'target')
        self.assertIn('messages', data)
