import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

from .models import CustomUser, Company, Invitation
from .views import UsersList, CompanyUsersList


class UsersTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.company_user = CustomUser.objects.create(
            username="company_user", email="company@company.com"
        )
        self.company = Company.objects.create(
            user=self.company_user, name="test_company"
        )
        self.user = CustomUser.objects.create(
            username="test", email="test@whatever.com"
        )

    def test_users_list(self):
        """
        List total non company users
        """
        view = UsersList.as_view()
        url = reverse("users")
        request = self.factory.get(url, {})

        # normal user shouldn't be able to access the users list
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # company user should be able to retrieve only non company users
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)  # only one user is returned
        self.assertFalse(data[0]["is_company"])
        self.assertEqual(data[0]["username"], self.user.username)

    def test_confirmed_company_users(self):
        view = CompanyUsersList.as_view()
        url = reverse("confirmed_users")
        request = self.factory.get(url, {})

        # normal user shouldn't be able to access the users list
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # company user should be able to retrieve only non company users
        _ = Invitation.objects.create(
            company=self.company,
            user=self.user,
        )
        force_authenticate(
            request, user=self.company_user, token=self.company_user.auth_token
        )
        response = view(request)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
