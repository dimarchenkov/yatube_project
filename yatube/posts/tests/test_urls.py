from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from ..models import Post, Group, User


class StaticURLTests(TestCase):
    """Static URL Tests"""
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    """Post Urls testing"""
    @classmethod
    def setUpClass(cls):
        """Create test db for user and group"""
        super().setUpClass()

        cls.user_author = User.objects.create_user(username='Some_user')

        cls.group = Group.objects.create(
            title='Группа поклонников графа',
            slug='fatmanoops',
            description='Толстой - супермен',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Новый пост без группы',
        )

        cls.templates_url_public = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user_author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }

        cls.templates_url_names_need_auth = {
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        cls.templates_url_list = {
            **cls.templates_url_public,
            **cls.templates_url_names_need_auth
        }

    def setUp(self):
        """Create clients."""
        self.guest = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.user = User.objects.create_user(username='Some_new_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_unauthorized_guest_urls_status_code(self):
        """Test status_code for unauthorized user."""
        for url in self.templates_url_public.keys():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_author_user_urls_status_code(self):
        """Test status_code for authorized author."""
        for url in self.templates_url_list.keys():
            with self.subTest(url=url):
                self.assertEqual(
                    self.post_author.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_urls_uses_correct_template(self):
        """Test templates."""
        cache.clear()
        for url, template in self.templates_url_list.items():
            with self.subTest(url=url):
                response = self.post_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_not_author_users_redirect(self):
        """Test redirect guest"""
        self.assertRedirects(
            self.guest.get(f'/posts/{self.post.id}/edit/'),
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            self.guest.get('/create/'),
            '/auth/login/?next=/create/'
        )
        self.assertRedirects(
            self.guest.get('/follow/'),
            '/auth/login/?next=/follow/'
        )

    def test_author_edit_wrong_post(self):
        """Test author try edit not own post"""
        self.assertRedirects(
            self.authorized_client.get(f'/posts/{self.post.id}/edit/'),
            f'/posts/{self.post.id}/'
        )

    def test_custom_404_template(self):
        """Test custom 404 template"""
        response_auth = self.post_author.get('/unexisting_page/')
        self.assertTemplateUsed(response_auth, 'core/404.html')

        response_guest = self.guest.get('/unexisting_page/')
        self.assertTemplateUsed(response_guest, 'core/404.html')
