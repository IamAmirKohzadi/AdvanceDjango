from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Task,TaskComment
from tasks.services import create_task_with_first_comment
from unittest.mock import patch

User = get_user_model()


class TaskAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="u1@test.com", password="Mam54321")
        self.user2 = User.objects.create_user(email="u2@test.com", password="Mam54321")

        self.list_url = reverse("task-list")

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

    def auth(self, user):
        token_url = reverse("token_obtain_pair")
        res = self.client.post(
            token_url, {"email": user.email, "password": "Mam54321"}, format="json"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_create_task_require_auth(self):
        res = self.client.post(
            self.list_url,
            {"title": "t", "description": "a", "status": Task.Status.TODO},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_authenticated(self):
        self.auth(self.user1)
        data = {"title": "New task", "description": "x", "status": Task.Status.TODO}
        res = self.client.post(self.list_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(owner=self.user1).count(), 2)

    def test_list_only_user_tasks(self):
        self.auth(self.user1)
        res = self.client.get(self.list_url)
        titles = [item["title"] for item in res.data["results"]]
        self.assertIn("Write docs", titles)
        self.assertNotIn("this is a book!", titles)

    def test_task_list_query_baseline(self):
        # Query baseline after adding owner_email and select_related optimization.
        cache.clear()
        self.auth(self.user1)
        for i in range(30):
            Task.objects.create(
                owner=self.user1,
                title=f"Write docs{i}",
                description=f"README work{i}",
                status=Task.Status.TODO,
                due_date=timezone.now() + timedelta(days=i),
            )
        with CaptureQueriesContext(connection) as ctx:
            res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(ctx.captured_queries), 4)

    def test_task_list_query_count_baseline(self):
        self.auth(self.user1)
        with self.assertNumQueries(4):
            res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_task_list_query_count_with_owner_email(self):
        cache.clear()
        self.auth(self.user1)
        for i in range(30):
            Task.objects.create(
                owner=self.user1,
                title=f"Write docs{i}",
                description=f"README work{i}",
                status=Task.Status.TODO,
                due_date=timezone.now() + timedelta(days=i),
            )
        with CaptureQueriesContext(connection) as ctx:
            res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(ctx.captured_queries), 4)

    def test_owner_can_update(self):
        self.auth(self.user1)
        details_url = reverse("task-detail", args=[self.task1.id])
        res = self.client.patch(details_url, {"title": "test update!"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_update(self):
        self.auth(self.user2)
        details_url = reverse("task-detail", args=[self.task1.id])
        res = self.client.patch(details_url, {"title": "updated post!"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_delete_task(self):
        self.auth(self.user1)
        detail_url = reverse("task-detail", args=[self.task1.id])

        res = self.client.delete(detail_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    def test_non_owner_cannot_delete_task(self):
        self.auth(self.user1)
        detail_url = reverse("task-detail", args=[self.task2.id])

        res = self.client.delete(detail_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=self.task2.id).exists())

    def test_list_filter_by_status(self):
        self.auth(self.user1)
        res = self.client.get(self.list_url, {"status": Task.Status.TODO})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertTrue(len(results) >= 1)
        self.assertTrue(all(item["status"] == Task.Status.TODO for item in results))

    def test_list_filter_by_search_title(self):
        self.auth(self.user1)
        res = self.client.get(self.list_url, {"search": "Write"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertTrue(len(results) >= 1)
        self.assertTrue(any(item["title"] == "Write docs" for item in results))

    def test_list_filter_by_search_description(self):
        self.auth(self.user1)
        res = self.client.get(self.list_url, {"search": "README"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertTrue(len(results) >= 1)
        self.assertTrue(any("README" in item["description"] for item in results))

    def test_ordering_created_date_asc(self):
        self.auth(self.user1)
        Task.objects.create(
            owner=self.user1,
            title="Write docs2",
            description="README work2",
            status=Task.Status.TODO,
            due_date=timezone.now() + timedelta(days=2),
        )
        res = self.client.get(self.list_url, {"ordering": "created_date"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        dates = [item["created_date"] for item in res.data["results"]]
        self.assertEqual(dates, sorted(dates))

    def test_ordering_created_date_desc(self):
        self.auth(self.user2)
        Task.objects.create(
            owner=self.user2,
            title="this is a book2!",
            description="the book is awesome2",
            status=Task.Status.TODO,
            due_date=timezone.now() + timedelta(days=2),
        )
        res = self.client.get(self.list_url, {"ordering": "-created_date"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        dates = [item["created_date"] for item in res.data["results"]]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_throttle_create(self):
        cache.clear()
        throttle_user_create = User.objects.create_user(
            email="u3@test.com", password="Mam54321"
        )
        self.auth(throttle_user_create)

        for i in range(20):
            res = self.client.post(
                self.list_url,
                {
                    "title": f"task{i}",
                    "description": f"description number {i}",
                    "status": Task.Status.TODO,
                },
                format="json",
            )
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(
            self.list_url,
            {
                "title": "throttle limit",
                "description": "limit hit!",
                "status": Task.Status.TODO,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_throttle_update(self):
        cache.clear()
        throttle_user_update = User.objects.create_user(
            email="u4@test.com", password="Mam54321"
        )
        self.auth(throttle_user_update)
        task = Task.objects.create(
            owner=throttle_user_update,
            title="task task 1",
            description="description number 1",
            status=Task.Status.TODO,
        )
        self.assertTrue(Task.objects.filter(id=task.id).exists())
        details_url = reverse("task-detail", args=[task.id])
        for i in range(20):
            res = self.client.patch(
                details_url, {"title": f"updated post{i}!"}, format="json"
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)
        res2 = self.client.patch(
            details_url, {"title": "throttle hit!"}, format="json"
        )
        self.assertEqual(res2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_task_list_query_count_with_comments(self):
        cache.clear()
        self.auth(self.user1)
        for i in range(10):
            Task.objects.create(
            owner=self.user1,
            title=f"Write docs{i}",
            description=f"README work{i}",
            status=Task.Status.TODO,
            due_date=timezone.now() + timedelta(days=i),
        )
        created_tasks = Task.objects.filter(owner=self.user1).order_by('-id')[:10]
        comments = []
        for index,t in enumerate(created_tasks):
            comments.append(TaskComment(task=t,author=self.user1,body=f'content number{index}'))
            comments.append(TaskComment(task=t,author=self.user1,body=f'content number{index + 1}'))
        TaskComment.objects.bulk_create(comments)
        with CaptureQueriesContext(connection) as ctx:
            res = self.client.get(self.list_url)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(ctx.captured_queries),5)

    def test_stats_require_auth(self):
        url = reverse('task-stats')
        res = self.client.get(url)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_stats_for_normal_user_is_owner_scoped(self):
        Task.objects.create(
            owner=self.user1,
            title="u1 in progress overdue",
            status=Task.Status.IN_PROGRESS,
            due_date=timezone.now() - timedelta(days=1),
        )
        Task.objects.create(
            owner=self.user1,
            title="u1 done overdue",
            status=Task.Status.DONE,
            due_date=timezone.now() - timedelta(days=2),
        )
        Task.objects.create(
            owner=self.user2,
            title="u2 todo overdue",
            status=Task.Status.TODO,
            due_date=timezone.now() + timedelta(days=1),
        )
        self.auth(self.user1)
        url = reverse("task-stats")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total tasks"], 3)  # self.task1 + 2 new for user1
        self.assertEqual(res.data["by_status"].get(Task.Status.TODO), 1)
        self.assertEqual(res.data["by_status"].get(Task.Status.IN_PROGRESS), 1)
        self.assertEqual(res.data["by_status"].get(Task.Status.DONE), 1)
        self.assertEqual(res.data["over_due"], 1)

    def test_stats_for_staff_user_sees_all_tasks(self):
        staff = User.objects.create_user(email="staff@test.com", password="Mam54321")
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        
        
        Task.objects.create(
            owner=self.user1,
            title="u1 task",
            status=Task.Status.TODO,
        )
        Task.objects.create(
            owner=self.user2,
            title="u2 task",
            status=Task.Status.IN_PROGRESS,
        )

        self.auth(staff)
        url = reverse("task-stats")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total tasks"], Task.objects.count())

class TaskServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='service@test.com',
            password='Mam54321'
        )

    def test_create_task_with_first_comment_success(self):
        task = create_task_with_first_comment(
            owner=self.user,
            title="Service task",
            description="Created from service",
            status=Task.Status.TODO,
            comment_body="First comment",
        )
        self.assertEqual(Task.objects.count(),1)
        self.assertEqual(TaskComment.objects.count(),1)

        self.assertEqual(task.owner , self.user)
        self.assertEqual(task.title,"Service task")
        self.assertTrue(TaskComment.objects.filter(task=task,body='First comment').exists())

    @patch("tasks.services.TaskComment.objects.create", side_effect=Exception("boom"))
    def test_create_task_with_comment_rolls_back(self, _):
        with self.assertRaises(Exception):
            create_task_with_first_comment(
                owner=self.user,
                title="Atomic test",
                comment_body="first",
            )
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(TaskComment.objects.count(), 0)
        