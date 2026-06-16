import json
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, PostPhoto
from photos.models import Photo
from users.models import User

class ListOfPostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_list_of_posts_success(self):
        # Create a post with an author
        Post.objects.create(title='Post 1', description='Description 1', author=self.user)
        
        # Create a post without an author
        Post.objects.create(title='Post 2', description='Description 2', author=None)
        
        # Create a photo with an s3_key
        photo1 = Photo.objects.create(s3_key='key1.jpg')
        post3 = Post.objects.create(title='Post 3', description='Description 3', author=self.user)
        PostPhoto.objects.create(post=post3, photo=photo1)
        
        # Create a photo without an s3_key
        photo2 = Photo.objects.create(s3_key=None)
        post4 = Post.objects.create(title='Post 4', description='Description 4', author=self.user)
        PostPhoto.objects.create(post=post4, photo=photo2)

        response = self.client.get(reverse('posts')) # name='posts' is used for list/ in urls.py
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('posts', data)
        self.assertEqual(len(data['posts']), 4)
        
        # Verify Post 2 (no author)
        post2_data = next(p for p in data['posts'] if p['title'] == 'Post 2')
        self.assertIsNone(post2_data['author'])
        
        # Verify Post 4 (photo with no s3_key)
        post4_data = next(p for p in data['posts'] if p['title'] == 'Post 4')
        self.assertEqual(len(post4_data['photos']), 0)
        
        # Verify Post 3 (photo with s3_key)
        post3_data = next(p for p in data['posts'] if p['title'] == 'Post 3')
        self.assertEqual(len(post3_data['photos']), 1)
        self.assertTrue(post3_data['photos'][0].endswith('key1.jpg'))
