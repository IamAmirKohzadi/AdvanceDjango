from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Task

User = get_user_model()

class TaskAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='u1@test.com', password='Mam54321')
        self.user2 = User.objects.create_user(email='u2@test.com', password='Mam54321')

        self.list_url = reverse('task-list')

        self.task1 = Task.objects.create(
            owner=self.user1,
            title="Write docs",
            description="README work",
            status=Task.Status.TODO,
            due_date=timezone.now() + timedelta(days=1),
        )
        self.task2 = Task.objects.create(
            owner=self.user2,
            title="this is a book!",
            description="the book is awesome!",
            status=Task.Status.DONE,
            due_date=timezone.now() + timedelta(days=2),
        )
    
    def auth(self,user):
        token_url = reverse('token_obtain_pair')
        res = self.client.post(token_url,{'email':user.email,'password' : 'Mam54321'},format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


    def test_create_task_require_auth(self):
        res = self.client.post(self.list_url,{
            'title':'t',
            'description':'a',
            'status':'Task.Status.TODO'
        },format='json')
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_create_task_authenticated(self):
        self.auth(self.user1)
        data =  {"title": "New task", "description": "x", "status": Task.Status.TODO}
        res = self.client.post(self.list_url,data,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(owner=self.user1).count(),2)
        
    def test_list_only_user_tasks(self):
        self.auth(self.user1)
        res = self.client.get(self.list_url)
        titles = [item['title'] for item in res.data['results']]
        self.assertIn('Write docs',titles)
        self.assertNotIn('this is a book!',titles)

    def test_non_owner_cannot_update(self):
        self.auth(self.user2)
        details_url = reverse('task-detail',args=[self.task1.id])
        res = self.client.patch(details_url,{'title' : 'updated post!'},format='json')
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)