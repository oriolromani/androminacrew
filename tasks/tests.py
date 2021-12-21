from datetime import datetime, timedelta
import pytz
import json

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from tasks.models import Task, WorkTime
from users.models import Company, CustomUser
from tasks.views import TaskList, WorkTimeCreation, WorkTimeDetail


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

    def test_task_work_times(self):
        """
        Test list work times of a task
        """
        work_time = WorkTime.objects.create(
            task=self.task_1,
        )
        view = TaskList.as_view()
        url = reverse("tasks")
        request = self.factory.get(url, {})

        # user should see its task work times
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]["times"]), 1)
        self.assertEqual(
            data[0]["times"][0]["start_time"],
            work_time.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def test_create_task_work_time(self):
        """
        Test create a task work time
        """
        view = WorkTimeCreation.as_view()
        url = reverse("work_time_creation", kwargs={"uid": self.task_1.uid})
        request = self.factory.post(url, {})
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request, self.task_1.pk)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(WorkTime.objects.filter(id=data["id"]).exists())

    def test_update_work_time(self):
        """
        Test update work time
        """
        work_time = WorkTime.objects.create(
            task=self.task_1,
        )
        view = WorkTimeDetail.as_view()
        url = reverse(
            "work_time_detail", kwargs={"pk": work_time.pk, "uid": self.task_1}
        )
        end_time = datetime.now(tz=pytz.UTC)
        data = {"end_time": end_time}
        request = self.factory.put(url, data=data)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request, uid=self.task_1.uid, pk=work_time.pk)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(data["end_time"], end_time.strftime("%Y-%m-%d %H:%M:%S"))

    def test_task_time(self):
        """
        Test sum of work times of a task is correct
        """
        task = Task.objects.create(
            company=self.company,
            name="test times",
            start_date=datetime.now(tz=pytz.UTC).date(),
            user=self.user,
        )
        start_time = datetime.now(tz=pytz.UTC)
        end_time = start_time + timedelta(seconds=361)
        _ = WorkTime.objects.create(
            start_time=start_time,
            end_time=end_time,
            task=task,
        )
        _ = WorkTime.objects.create(
            start_time=start_time,
            task=task,
        )
        # only first work_time should be considered to compute task time
        task = Task.objects.get(pk=task.pk)
        self.assertEqual(6, task.time)
