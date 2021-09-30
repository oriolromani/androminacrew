from datetime import datetime, timedelta
import pytz
import json

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from tasks.models import Task
from users.models import Company
from tasks.views import TaskList


class TasksTests(APITestCase):
    def test_list_tasks(self):
        """
        List tasks according to user
        """
        factory = APIRequestFactory()
        view = TaskList.as_view()
        company_user = User.objects.create(username="company_user")
        company = Company.objects.create(user=company_user, name="test_company")
        admin_user = User.objects.create(username="admin")
        admin_user.is_staff = True
        admin_user.save()
        task_1 = Task.objects.create(
            company=company,
            name="test",
            start_time=datetime.now(tz=pytz.UTC) + timedelta(days=1),
            end_time=datetime.now(tz=pytz.UTC) + timedelta(days=2),
        )
        user = User.objects.create(username="test")
        url = reverse("tasks")
        request = factory.get(url, {})

        # company user should see its task
        force_authenticate(request, user=company_user, token=company_user.auth_token)
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], task_1.name)

        # admin user should see all tasks
        force_authenticate(request, user=admin_user, token=admin_user.auth_token)
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], task_1.name)

        # normal user should only see its tasks
        force_authenticate(request, user=user, token=user.auth_token)
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)
