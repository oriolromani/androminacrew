from datetime import datetime, timedelta
import pytz
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from tasks.models import Task
from users.models import Company, CustomUser
from tasks.views import TaskList, CreateUserTask


class TasksTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.company_user = CustomUser.objects.create(
            username="company_user", email="company@company.com"
        )
        self.company = Company.objects.create(
            user=self.company_user, name="test_company"
        )
        self.admin_user = CustomUser.objects.create(
            username="admin", email="admin@androminacrew.com"
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.task_1 = Task.objects.create(
            company=self.company,
            name="test",
            start_time=datetime.now(tz=pytz.UTC) + timedelta(days=1),
            end_time=datetime.now(tz=pytz.UTC) + timedelta(days=2),
        )
        self.user = CustomUser.objects.create(
            username="test", email="test@whatever.com"
        )

    def test_list_tasks(self):
        """
        List tasks according to user
        """
        view = TaskList.as_view()
        url = reverse("tasks")
        request = self.factory.get(url, {})

        # company user should see its task
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.task_1.name)

        # admin user should see all tasks
        force_authenticate(
            request, user=self.admin_user, token=self.admin_user.auth_token
        )
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.task_1.name)

        # normal user should only see its tasks
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_create_task(self):
        """
        Company user should be able to create tasks
        """
        view = TaskList.as_view()
        url = reverse("tasks")
        data = {
            "name": "task_2",
            "start_time": datetime.now(tz=pytz.UTC) + timedelta(days=1),
            "end_time": datetime.now(tz=pytz.UTC) + timedelta(days=2),
        }
        request = self.factory.post(url, data)

        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertTrue(Task.objects.filter(name="task_2").exists())  # task is created

        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Task.objects.count(), 2
        )  # same than previous post by a customer user

    def test_create_user_task_by_normal_user(self):
        """
        Normal user shouldn't be able to create a UserTask
        """
        view = CreateUserTask.as_view()
        normal_user = CustomUser.objects.create(username="normal")
        url = reverse("user_tasks")
        data = {"user": self.user.uid, "task_id": self.task_1.id}
        request = self.factory.post(url, data)
        force_authenticate(request, user=normal_user, token=normal_user.auth_token)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_task_company_user(self):
        """
        Company user should be able to create a UserTask a.k.a. propose
        a task to a user
        """
        view = CreateUserTask.as_view()
        url = reverse("user_tasks")
        data = {"user": self.user.uid, "task": self.task_1.id}
        request = self.factory.post(url, data)
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
