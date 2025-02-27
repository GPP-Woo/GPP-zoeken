from django.urls import path

from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.test import APITestCase, URLPatternsTestCase

from ..authorization import TokenAuthentication
from ..permissions import TokenAuthPermission, TokenAuthReadPermission
from .factories import TokenAuthFactory


class TestAutorizationAndPermissionView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (TokenAuthPermission,)

    """
    A simple ViewSet for listing or retrieving users.
    """

    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestAutorizationAndReadPermissionView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (TokenAuthReadPermission,)

    """
    A simple ViewSet for listing or retrieving users.
    """

    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_201_CREATED)


class ApiTokenAuthorizationAndPermissionTests(URLPatternsTestCase, APITestCase):
    urlpatterns = [
        path("whatever", TestAutorizationAndPermissionView.as_view()),
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.no_permission_token = TokenAuthFactory.create(permissions=[]).token
        cls.read_token = TokenAuthFactory.create(read_permission=True).token
        cls.write_token = TokenAuthFactory.create(write_permission=True).token
        cls.read_write_token = TokenAuthFactory.create(read_write_permission=True).token

    def test_get_endpoint(self):
        with self.subTest("no token given"):
            response = self.client.get("/whatever")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("none existing token"):
            response = self.client.get(
                "/whatever", headers={"Authorization": "Token broken"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("token with no permission"):
            response = self.client.get(
                "/whatever",
                headers={"Authorization": f"Token {self.no_permission_token}"},
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with wrong permission"):
            response = self.client.get(
                "/whatever", headers={"Authorization": f"Token {self.write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with correct permission"):
            response = self.client.get(
                "/whatever", headers={"Authorization": f"Token {self.read_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("token with all permissions"):
            response = self.client.get(
                "/whatever", headers={"Authorization": f"Token {self.read_write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_endpoint(self):
        with self.subTest("no token given"):
            response = self.client.post("/whatever")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("none existing token"):
            response = self.client.post(
                "/whatever", headers={"Authorization": "Token broken"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("token with no permission"):
            response = self.client.post(
                "/whatever",
                headers={"Authorization": f"Token {self.no_permission_token}"},
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with wrong permission"):
            response = self.client.post(
                "/whatever", headers={"Authorization": f"Token {self.read_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with correct permission"):
            response = self.client.post(
                "/whatever", headers={"Authorization": f"Token {self.write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        with self.subTest("token with all permissions"):
            response = self.client.post(
                "/whatever", headers={"Authorization": f"Token {self.read_write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_endpoint(self):
        with self.subTest("no token given"):
            response = self.client.put("/whatever")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("none existing token"):
            response = self.client.put(
                "/whatever", headers={"Authorization": "Token broken"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("token with no permission"):
            response = self.client.put(
                "/whatever",
                headers={"Authorization": f"Token {self.no_permission_token}"},
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with wrong permission"):
            response = self.client.put(
                "/whatever", headers={"Authorization": f"Token {self.read_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with correct permission"):
            response = self.client.put(
                "/whatever", headers={"Authorization": f"Token {self.write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("token with all permissions"):
            response = self.client.put(
                "/whatever", headers={"Authorization": f"Token {self.read_write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_endpoint(self):
        with self.subTest("no token given"):
            response = self.client.delete("/whatever")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("none existing token"):
            response = self.client.delete(
                "/whatever", headers={"Authorization": "Token broken"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("token with no permission"):
            response = self.client.delete(
                "/whatever",
                headers={"Authorization": f"Token {self.no_permission_token}"},
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with wrong permission"):
            response = self.client.delete(
                "/whatever", headers={"Authorization": f"Token {self.read_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with correct permission"):
            response = self.client.delete(
                "/whatever", headers={"Authorization": f"Token {self.write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.subTest("token with all permissions"):
            response = self.client.delete(
                "/whatever", headers={"Authorization": f"Token {self.read_write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ApiTokenAuthorizationAndReadPermissionTests(URLPatternsTestCase, APITestCase):
    urlpatterns = [
        path("whatever", TestAutorizationAndReadPermissionView.as_view()),
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.no_permission_token = TokenAuthFactory.create(permissions=[]).token
        cls.read_token = TokenAuthFactory.create(read_permission=True).token
        cls.write_token = TokenAuthFactory.create(write_permission=True).token
        cls.read_write_token = TokenAuthFactory.create(read_write_permission=True).token

    def test_get_endpoint(self):
        with self.subTest("no token given"):
            response = self.client.get("/whatever")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("none existing token"):
            response = self.client.get(
                "/whatever", headers={"Authorization": "Token broken"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("token with no permission"):
            response = self.client.get(
                "/whatever",
                headers={"Authorization": f"Token {self.no_permission_token}"},
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with wrong permission"):
            response = self.client.get(
                "/whatever", headers={"Authorization": f"Token {self.write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with correct permission"):
            response = self.client.get(
                "/whatever", headers={"Authorization": f"Token {self.read_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("token with all permissions"):
            response = self.client.get(
                "/whatever", headers={"Authorization": f"Token {self.read_write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_endpoint(self):
        with self.subTest("no token given"):
            response = self.client.post("/whatever")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("none existing token"):
            response = self.client.post(
                "/whatever", headers={"Authorization": "Token broken"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("token with no permission"):
            response = self.client.post(
                "/whatever",
                headers={"Authorization": f"Token {self.no_permission_token}"},
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with wrong permission"):
            response = self.client.post(
                "/whatever", headers={"Authorization": f"Token {self.write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("token with correct permission"):
            response = self.client.post(
                "/whatever", headers={"Authorization": f"Token {self.read_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        with self.subTest("token with all permissions"):
            response = self.client.post(
                "/whatever", headers={"Authorization": f"Token {self.read_write_token}"}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
