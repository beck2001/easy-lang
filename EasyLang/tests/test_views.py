from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from mainApp.models import *
from mainApp.views import *

class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            tg_id = 123,
            name = 'John',
            surname = 'Doe',
            password = 'password123'
        )
        self.editor = Editor.objects.create(user=self.user)
        self.translator = Translator.objects.create(user=self.user)
        self.manager = Manager.objects.create(user=self.user)
        self.project = Project.objects.create(
            name='Test Project', description='Test Description', deadline='2023-12-31', manager=self.manager, total_pages_count=100)
        self.project_editor = Project_Editor.objects.create(
            project=self.project, editor=self.editor, active=True)
        self.project_translator = Project_Translator.objects.create(
            project=self.project, translator=self.translator, active=True)


    def test_free_editors_list_view(self):
        # Test free editors list view
        response = self.client.get(
            reverse('free_editors_list') + f'?project_id={self.project.id}')
        self.assertEqual(response.status_code, 302)


    # Similar tests for other views...

    def test_appoint_editor_view(self):
        # Test appoint editor view behavior
        response = self.client.post(reverse('appoint_editor'), {
            'project_id': self.project.id,
            'role_user_id': self.user.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect to 'home'
        self.assertEqual(Project_Editor.objects.filter(
            project=self.project, editor=self.editor).count(), 1)

    def test_index_unlogged_view(self):
        # Test index view behavior
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'index.html')