from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import FamousPerson, CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
import os

# Create your tests here.

class FamousPersonModelTest(TestCase):
    def setUp(self):
        # Create a test image file
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )
        
        # Create test famous people
        self.person1 = FamousPerson.objects.create(
            name="Test Person 1",
            image=self.test_image,
            difficulty="easy",
            skin_color="light"
        )
        self.person2 = FamousPerson.objects.create(
            name="Test Person 2",
            image=self.test_image,
            difficulty="medium",
            skin_color="dark"
        )

    def test_famous_person_creation(self):
        """Test that FamousPerson objects are created correctly"""
        self.assertEqual(self.person1.name, "Test Person 1")
        self.assertEqual(self.person1.difficulty, "easy")
        self.assertEqual(self.person1.skin_color, "light")
        self.assertTrue(isinstance(self.person1, FamousPerson))

    def test_famous_person_str(self):
        """Test the string representation of FamousPerson"""
        self.assertEqual(str(self.person1), "Test Person 1")

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.person1.image.path):
            os.remove(self.person1.image.path)
        if os.path.exists(self.person2.image.path):
            os.remove(self.person2.image.path)

class QuizViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a CustomUser instead of regular User
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test images
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )
        
        # Create test famous people
        self.person1 = FamousPerson.objects.create(
            name="Test Person 1",
            image=self.test_image,
            difficulty="easy",
            skin_color="light"
        )
        self.person2 = FamousPerson.objects.create(
            name="Test Person 2",
            image=self.test_image,
            difficulty="easy",
            skin_color="dark"
        )

    def test_quiz_page_load(self):
        """Test that quiz page loads correctly"""
        response = self.client.get(reverse('quiz', kwargs={'difficulty': 'easy'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz_page.html')

    def test_quiz_session_score(self):
        """Test that session score is initialized correctly"""
        response = self.client.get(reverse('quiz', kwargs={'difficulty': 'easy'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('session_score', response.context)
        self.assertEqual(response.context['session_score'], 0)

    def test_correct_answer(self):
        """Test handling of correct answer"""
        # First get the quiz page to initialize session
        self.client.get(reverse('quiz', kwargs={'difficulty': 'easy'}))
        
        # Get the correct answer from the session
        session = self.client.session
        correct_index = session.get('correct_image_index')
        
        # Submit correct answer
        response = self.client.post(
            reverse('quiz', kwargs={'difficulty': 'easy'}),
            {'selected_index': correct_index},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('new_session_score', response.json())
        self.assertEqual(response.json()['new_session_score'], 1)

    def test_wrong_answer(self):
        """Test handling of wrong answer"""
        # First get the quiz page to initialize session
        self.client.get(reverse('quiz', kwargs={'difficulty': 'easy'}))
        
        # Get the correct answer from the session
        session = self.client.session
        correct_index = session.get('correct_image_index')
        wrong_index = 1 if correct_index == 0 else 0
        
        # Submit wrong answer
        response = self.client.post(
            reverse('quiz', kwargs={'difficulty': 'easy'}),
            {'selected_index': wrong_index},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('game_over', response.json())
        self.assertTrue(response.json()['game_over'])

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.person1.image.path):
            os.remove(self.person1.image.path)
        if os.path.exists(self.person2.image.path):
            os.remove(self.person2.image.path)

class DifficultyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a CustomUser instead of regular User
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_difficulty_page_load(self):
        """Test that difficulty selection page loads correctly"""
        response = self.client.get(reverse('difficulty'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'difficulty.html')

    def test_difficulty_links(self):
        """Test that difficulty links are present"""
        response = self.client.get(reverse('difficulty'))
        self.assertContains(response, 'easy')
        self.assertContains(response, 'medium')
        self.assertContains(response, 'hard')
