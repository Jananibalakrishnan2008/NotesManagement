from django.test import TestCase, Client
from django.urls import reverse
from .models import Note


class NoteManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.note1 = Note.objects.create(
            title="Django Setup Guide",
            content="Step 1: Install django. Step 2: run migrations.",
            category="Study",
            is_favorite=False
        )
        self.note2 = Note.objects.create(
            title="Grocery Shopping List",
            content="Apples, Milk, Bread, Coffee.",
            category="Personal",
            is_favorite=True
        )
        self.note3 = Note.objects.create(
            title="Client Project Architecture",
            content="Microservices and REST APIs.",
            category="Project",
            is_favorite=False
        )

    def test_home_view_loads_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NotesFlow")
        self.assertEqual(response.context['total_notes'], 3)
        self.assertEqual(response.context['study_count'], 1)
        self.assertEqual(response.context['personal_count'], 1)
        self.assertEqual(response.context['project_count'], 1)
        self.assertEqual(response.context['favorites_count'], 1)

    def test_search_notes(self):
        # Search for "Grocery"
        response = self.client.get(reverse('home') + '?search=Grocery')
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.note2, notes)
        self.assertNotIn(self.note1, notes)

    def test_category_filter(self):
        # Filter by Study
        response = self.client.get(reverse('home') + '?category=Study')
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.note1, notes)
        self.assertNotIn(self.note2, notes)

    def test_favorites_filter(self):
        # Filter by Favorite
        response = self.client.get(reverse('home') + '?favorite=1')
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertIn(self.note2, notes)
        self.assertNotIn(self.note1, notes)

    def test_sorting(self):
        response = self.client.get(reverse('home') + '?sort=title_asc')
        self.assertEqual(response.status_code, 200)
        notes = list(response.context['notes'])
        self.assertEqual(notes[0].title, "Client Project Architecture")

    def test_add_note_success(self):
        response = self.client.post(reverse('add_note'), {
            'title': 'New Test Note',
            'content': 'This is a brand new test note content.',
            'category': 'Work',
            'is_favorite': 'on'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Note.objects.filter(title='New Test Note').exists())
        created_note = Note.objects.get(title='New Test Note')
        self.assertTrue(created_note.is_favorite)
        self.assertEqual(created_note.category, 'Work')

    def test_add_note_validation_failure(self):
        response = self.client.post(reverse('add_note'), {
            'title': '',
            'content': '',
            'category': 'Work'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 3)

    def test_view_note_html_and_ajax(self):
        # Standalone HTML view
        response = self.client.get(reverse('view_note', args=[self.note1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Setup Guide")

        # JSON / AJAX view for modal
        response_json = self.client.get(reverse('view_note', args=[self.note1.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_json.status_code, 200)
        data = response_json.json()
        self.assertEqual(data['title'], "Django Setup Guide")
        self.assertEqual(data['category'], "Study")

    def test_edit_note(self):
        response = self.client.post(reverse('edit_note', args=[self.note1.id]), {
            'title': 'Updated Title',
            'content': 'Updated Content',
            'category': 'Personal',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Updated Title')
        self.assertEqual(self.note1.category, 'Personal')

    def test_delete_note(self):
        response = self.client.post(reverse('delete_note', args=[self.note1.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Note.objects.filter(id=self.note1.id).exists())

    def test_toggle_favorite(self):
        # AJAX toggle
        response = self.client.post(reverse('toggle_favorite', args=[self.note1.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_favorite'])
        self.note1.refresh_from_db()
        self.assertTrue(self.note1.is_favorite)
