from django.test import TestCase
from django.utils import timezone
from mainApp.models import User, Manager, Project, Translator, Editor, Project_Translator, Project_Editor, Pages_per_day, Approve, Disapprove

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

