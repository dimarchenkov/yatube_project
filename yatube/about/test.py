from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.templates_url_names = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech'
        }

    def test_about_url_guest_user(self):
        """Test about url guest user."""
        for reverse_name in self.templates_url_names.values():
            with self.subTest():
                response = self.guest_client.get(reverse(reverse_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_templates(self):
        """Test urls has correct templates."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(reverse_name))
                self.assertTemplateUsed(response, template)
