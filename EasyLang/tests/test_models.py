from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from mainApp.models import User, Manager, Project, Translator, Editor, Project_Translator, Project_Editor, Pages_per_day, Approve, Disapprove, UserManager
from datetime import date


class CreateUserTestCase(TestCase):

    def test_create_user_success(self):
        user = User.objects.create_user(tg_id=100, name="John", surname="Doe", password="password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "John")
        self.assertEqual(user.surname, "Doe")
        self.assertEqual(user.tg_id, 100)
        self.assertTrue(user.check_password("password123"))

    def test_create_user_no_tg_id(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(tg_id=None, name="John", surname="Doe", password="password123")

    def test_create_user_no_name(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(tg_id=101, name=None, surname="Doe", password="password123")

    def test_create_user_no_surname(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(tg_id=102, name="John", surname=None, password="password123")

    def test_create_user_no_password(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(tg_id=103, name="John", surname="Doe", password=None)


class CreateSuperuserTestCase(TestCase):

    def test_create_superuser_success(self):
        superuser = User.objects.create_superuser(tg_id=200, name="Admin", surname="User", password="adminpass")
        self.assertIsNotNone(superuser)
        self.assertEqual(superuser.name, "Admin")
        self.assertEqual(superuser.surname, "User")
        self.assertEqual(superuser.tg_id, 200)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.check_password("adminpass"))

    def test_create_superuser_no_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(tg_id=201, name="Admin", surname="User", password="adminpass", is_staff=False)

    def test_create_superuser_no_is_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(tg_id=202, name="Admin", surname="User", password="adminpass", is_superuser=False)


class ModelTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(tg_id=123, name='John', surname='Doe', password='password123')

        # Create a manager for testing
        self.manager = Manager.objects.create(user=self.user)

        # Create a project for testing
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            deadline=timezone.now() + timezone.timedelta(days=10),
            manager=self.manager,
            total_pages_count=100
        )

        # Create a translator for testing
        self.translator = Translator.objects.create(user=self.user)

        # Create an editor for testing
        self.editor = Editor.objects.create(user=self.user)

    def test_project_translator_str_method(self):
        project_translator = Project_Translator.objects.create(project=self.project, translator=self.translator)
        self.assertEqual(str(project_translator), 'John Doe Test Project')

    def test_project_editor_str_method(self):
        project_editor = Project_Editor.objects.create(project=self.project, editor=self.editor)
        self.assertEqual(str(project_editor), 'John Doe Test Project')

    def test_pages_per_day_str_method(self):
        pages_per_day = Pages_per_day.objects.create(translator=self.translator, project=self.project, pages_count=10)
        self.assertEqual(str(pages_per_day), 'John Doe Test Project 10')

    def test_approve_creation(self):
        pages_per_day = Pages_per_day.objects.create(translator=self.translator, project=self.project, pages_count=10)
        approve = Approve.objects.create(
            pages_per_day=pages_per_day,
            editor=self.editor,
            comment="Approved"
        )
        self.assertEqual(approve.pages_per_day, pages_per_day)
        self.assertEqual(approve.editor, self.editor)
        self.assertEqual(approve.comment, "Approved")

    def test_disapprove_creation(self):
        pages_per_day = Pages_per_day.objects.create(translator=self.translator, project=self.project, pages_count=10)
        disapprove = Disapprove.objects.create(
            pages_per_day=pages_per_day,
            editor=self.editor,
            comment="Disapproved"
        )
        self.assertEqual(disapprove.pages_per_day, pages_per_day)
        self.assertEqual(disapprove.editor, self.editor)
        self.assertEqual(disapprove.comment, "Disapproved")