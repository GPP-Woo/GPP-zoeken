from rest_framework import status
from rest_framework.test import APIClient

from .factories import TokenAuthFactory


class APIKeyUnAuthorizedMixin:
    client: APIClient

    def assertWrongApiKeyProhibitsPostEndpointAccess(self, url):
        no_permission_token = TokenAuthFactory.create(permissions=[]).token
        read_token = TokenAuthFactory.create(read_permission=True).token

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "no token given"
        ):
            response = self.client.post(url)
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "none existing token"
        ):
            response = self.client.post(url, headers={"Authorization": "Token broken"})
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "token with no permission"
        ):
            response = self.client.post(
                url,
                headers={"Authorization": f"Token {no_permission_token}"},
            )
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_403_FORBIDDEN
            )

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "token with wrong permission"
        ):
            response = self.client.post(
                url, headers={"Authorization": f"Token {read_token}"}
            )
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_403_FORBIDDEN
            )

    def assertWrongApiKeyProhibitsDeleteEndpointAccess(self, url):
        no_permission_token = TokenAuthFactory.create(permissions=[]).token
        read_token = TokenAuthFactory.create(read_permission=True).token

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "no token given"
        ):
            response = self.client.delete(url)
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "none existing token"
        ):
            response = self.client.delete(
                url, headers={"Authorization": "Token broken"}
            )
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "token with no permission"
        ):
            response = self.client.delete(
                url,
                headers={"Authorization": f"Token {no_permission_token}"},
            )
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_403_FORBIDDEN
            )

        with self.subTest(  # pyright: ignore[reportAttributeAccessIssue]
            "token with wrong permission"
        ):
            response = self.client.delete(
                url, headers={"Authorization": f"Token {read_token}"}
            )
            self.assertEqual(  # pyright: ignore[reportAttributeAccessIssue]
                response.status_code, status.HTTP_403_FORBIDDEN
            )


class TokenAuthMixin:
    client: APIClient

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()  # pyright: ignore[reportAttributeAccessIssue]

        cls.token_auth = TokenAuthFactory.create(read_write_permission=True)

    def setUp(self):
        super().setUp()  # pyright: ignore[reportAttributeAccessIssue]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_auth.token}")
