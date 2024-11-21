from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User
from snippets.models import Snippet, AuditRecord
from snippets.serializers import SnippetSerializer, AuditRecordSerializer


class UserManagementTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(username="staffuser", password="password", is_staff=True)
        self.regular_user = User.objects.create_user(username="regularuser", password="password", is_staff=False)
        self.user_to_delete = User.objects.create_user(username="usertodelete", password="password")

    def test_only_staff_can_create_user(self):
        # Authenticate as a regular user
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post("/users/create/", {"username": "newuser", "password": "newpassword"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as a staff user
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post("/users/create/", {"username": "newuser", "password": "newpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_only_staff_can_soft_delete_user(self):
        # Authenticate as a regular user
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete("/users/delete/", {"username": self.user_to_delete.username})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as a staff user
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete("/users/delete/", {"username": self.user_to_delete.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify soft delete (is_active is set to False)
        self.user_to_delete.refresh_from_db()
        self.assertFalse(self.user_to_delete.is_active)


class AuditRecordCreationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(username="staffuser", password="password", is_staff=True)
        self.regular_user = User.objects.create_user(username="regularuser", password="password", is_staff=False)
        self.client.force_authenticate(user=self.staff_user)  # Authenticate as staff user for user creation

    def test_audit_record_created_on_user_creation(self):
        # Create a user via the API
        response = self.client.post("/users/create/", {"username": "newuser", "password": "newpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that an audit record was created
        audit_record = AuditRecord.objects.filter(model_name="User", action="create").first()
        self.assertIsNotNone(audit_record)
        self.assertEqual(audit_record.user, self.staff_user)
        self.assertEqual(audit_record.model_name, "User")
        self.assertEqual(audit_record.action, "create")
        self.assertTrue(User.objects.filter(id=audit_record.object_id).exists())

    def test_audit_record_created_on_snippet_creation(self):
        # Authenticate as regular user for snippet creation
        self.client.force_authenticate(user=self.regular_user)

        # Create a snippet via the API
        snippet_data = {
            "title": "Test Snippet",
            "code": "print('Hello, world!')",
            "language": "python",
            "style": "friendly",
        }
        response = self.client.post("/snippets/", snippet_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that an audit record was created
        audit_record = AuditRecord.objects.filter(model_name="Snippet", action="create").first()
        self.assertIsNotNone(audit_record)
        self.assertEqual(audit_record.user, self.regular_user)
        self.assertEqual(audit_record.model_name, "Snippet")
        self.assertEqual(audit_record.action, "create")
        self.assertTrue(Snippet.objects.filter(id=audit_record.object_id).exists())


class TokenLoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.login_url = "/login/"

    def test_valid_login_returns_token(self):
        # Attempt to log in with valid credentials
        response = self.client.post(self.login_url, {"username": "testuser", "password": "password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        token = response.data["token"]
        self.assertTrue(len(token) > 0, "Token should not be empty.")

    def test_invalid_login_returns_error(self):
        # Attempt to log in with invalid credentials
        response = self.client.post(self.login_url, {"username": "testuser", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_credentials_returns_error(self):
        # Attempt to log in without providing credentials
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SnippetCreationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(username="staffuser", password="password", is_staff=True)
        self.regular_user = User.objects.create_user(username="regularuser", password="password", is_staff=False)
        self.snippet_data = {
            "title": "Test Snippet",
            "code": "print('Hello, world!')",
            "language": "python",
            "style": "friendly",
        }

    def test_staff_user_can_create_snippet(self):
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post("/snippets/", self.snippet_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Snippet.objects.count(), 1)
        snippet = Snippet.objects.first()
        self.assertEqual(snippet.owner, self.staff_user)
        self.assertEqual(snippet.title, self.snippet_data["title"])

    def test_regular_user_can_create_snippet(self):
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post("/snippets/", self.snippet_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Snippet.objects.count(), 1)
        snippet = Snippet.objects.first()
        self.assertEqual(snippet.owner, self.regular_user)
        self.assertEqual(snippet.title, self.snippet_data["title"])