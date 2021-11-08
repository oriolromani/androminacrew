from datetime import datetime, timedelta
import pytz
import json

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from tasks.models import Task, UserTask
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

        _ = UserTask.objects.create(user=self.user, task=self.task_1)
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)


class CreateTaskTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.company_user = CustomUser.objects.create(
            username="company_user", email="company@company.com"
        )
        self.company = Company.objects.create(
            user=self.company_user, name="test_company"
        )
        self.task_1 = Task.objects.create(
            company=self.company,
            name="test",
            start_time=datetime.now(tz=pytz.UTC) + timedelta(days=1),
            end_time=datetime.now(tz=pytz.UTC) + timedelta(days=2),
        )
        self.user = CustomUser.objects.create(
            username="test", email="test@whatever.com"
        )

    def test_create_non_existing_task(self):
        """
        Create a Task with no UserTasks
        """
        view = CreateUserTask.as_view()
        url = reverse("user_tasks")
        data = {
            "name": "test2",
            "start_time": datetime.now(tz=pytz.UTC) + timedelta(days=1),
            "end_time": datetime.now(tz=pytz.UTC) + timedelta(days=2),
        }
        request = self.factory.post(url, data=data)
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        _ = view(request)
        self.assertTrue(Task.objects.filter(name="test2").exists())

    def test_create_task_and_usertasks(self):
        """
        Create Task and UserTask
        """
        view = CreateUserTask.as_view()
        url = reverse("user_tasks")
        data = {
            "name": "test3",
            "start_time": datetime.now(tz=pytz.UTC) + timedelta(days=1),
            "end_time": datetime.now(tz=pytz.UTC) + timedelta(days=2),
            "users": [self.user.uid],
        }
        request = self.factory.post(url, data=data)
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        _ = view(request)
        self.assertTrue(UserTask.objects.filter(user=self.user).exists())

    def test_create_user_task_on_existing_task(self):
        """
        Create UserTask on exising Task
        """
        user_2 = CustomUser.objects.create(username="test2", email="test2@whatever.com")
        tasks_count_pre = Task.objects.count()
        view = CreateUserTask.as_view()
        url = reverse("user_tasks")
        data = {
            "name": self.task_1.name,
            "start_time": self.task_1.start_time,
            "end_time": self.task_1.end_time,
            "users": [user_2.uid],
            "uid": self.task_1.uid,
        }
        request = self.factory.post(url, data=data)
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        _ = view(request)
        self.assertTrue(UserTask.objects.filter(user=user_2).exists())
        # test no new task has been created
        self.assertEqual(tasks_count_pre, Task.objects.count())
