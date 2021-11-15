from datetime import datetime
import pytz
import json

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from tasks.models import Task
from users.models import Company, CustomUser
from tasks.views import TaskList


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
        self.user = CustomUser.objects.create(
            username="test", email="test@whatever.com"
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.task_1 = Task.objects.create(
            company=self.company,
            name="test",
            start_date=datetime.now(tz=pytz.UTC).date(),
            user=self.user,
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
        self.assertEqual(len(data), 1)
