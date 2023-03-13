from http import HTTPStatus
import shutil
import tempfile

from django import forms
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Group, Post, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Test post pages."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='fat-oops',
            description='TurboGroup',
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
            image=cls.image,
        )
        cls.comment_post = Comment.objects.create(
            author=cls.user,
            text='Мой первый комментарий',
            post=cls.post
        )
        cls.url_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
        ]

    @classmethod
    def tearDownClass(cls):
        """Delete test media."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.unauthorized_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_unauthorized_user_in(self):
        """Test unauthorized user in."""
        field_urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}
            ): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'
            ): 302,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.unauthorized_user.get(url).status_code
                self.assertEqual(status_code, response_code)

    def check_post_info(self, post):
        self.assertIsInstance(post, Post)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)
        self.assertEqual(post.image, self.post.image)
        self.assertEqual(post.comments.last(), self.comment_post)

    def test_forms_show_correct(self):
        """Test form correct."""
        context = {
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id, }),
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField
                )
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField
                )
                self.assertIsInstance(
                    response.context['form'].fields['image'],
                    forms.fields.ImageField
                )

    def test_is_edit_correct(self):
        """Tets var is edit correct."""
        response_post_edit = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id, })
        )
        self.assertTrue(response_post_edit.context.get('is_edit'))

    def test_index_page_show_correct_context(self):
        """Test context index.html."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post_info(response.context['page_obj'][0])

    def test_groups_page_show_correct_context(self):
        """Test contex group_list.html."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.check_post_info(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Text context profile.html."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.user)
        self.assertFalse(response.context['following'])
        self.check_post_info(response.context['page_obj'][0])

    def test_detail_page_show_correct_context(self):
        """Test context post_detail.html."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.check_post_info(response.context['post'])
        first_comment = response.context["comments"][0]
        self.assertEqual(first_comment, self.comment_post)

    def test_post_in_right_pages(self):
        """Test post places on right pages."""

        right_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            ),
        ]
        for url in right_pages:
            response = self.authorized_client.get(url)
            self.assertIn(
                self.post,
                response.context.get('page_obj'),
            )

    def test_post_is_not_in_wrong_group(self):
        """Test post is not in wrong group."""
        group_new = Group.objects.create(
            title='Новая группа',
            slug='other-group',
            description='Очень новыя группа'
        )
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=group_new,
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug})
        )
        all_objects = response.context['page_obj']
        self.assertNotIn(post, all_objects)

    def test_index_caches(self):
        """Test cache working on index page."""
        post_cache = Post.objects.create(
            author=self.user,
            text='Тестовый пост для проверки работы кэша',
        )
        url = reverse('posts:index')
        response_old = self.authorized_client.get(url)
        post_cache.delete()
        response = self.authorized_client.get(url)
        self.assertEqual(response.content, response_old.content)
        cache.clear()
        response_new = self.authorized_client.get(url)
        self.assertNotEqual(response.content, response_new.content)


class PaginatorViewsTest(TestCase):
    """Test paginator"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.OVER_PAGE_POSTS = 3

        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.posts = []
        for post_counter in range(
            settings.COUNT_PER_PAGE + cls.OVER_PAGE_POSTS
        ):
            cls.posts.append(Post(
                text=f'Тестовый пост {post_counter}',
                author=cls.user,
                group=cls.group
            ))
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Test paginator on pages."""
        cache.clear()
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for url in url_pages:
            with self.subTest(url=url):
                self.assertEqual(len(self.unauthorized_client.get(
                    url).context.get('page_obj')),
                    settings.COUNT_PER_PAGE
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    url + '?page=2').context.get('page_obj')),
                    self.OVER_PAGE_POSTS
                )


class FollowTest(TestCase):
    """Test followers."""
    @classmethod
    def setUpTestData(cls):
        """Setup db."""
        cls.author = User.objects.create(
            username='Author_1'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text'
        )
        cls.follower = User.objects.create(
            username='Follower_1'
        )

    def setUp(self) -> None:
        """Setup clients."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_add_follow(self):
        """Test auth user can follow up."""
        self.author_2 = User.objects.create(
            username='Author_2'
        )
        count_before = Follow.objects.filter(
            user=self.follower, author=self.author_2).count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.author_2.username,)
            )
        )
        self.assertEqual(
            Follow.objects.filter(
                user=self.follower, author=self.author_2).count(),
            count_before + 1
        )

        follow_last = Follow.objects.last()
        self.assertEqual(follow_last.author, self.author_2)
        self.assertEqual(follow_last.user, self.follower)

    def test_not_add_follow_for_non_auth(self):
        """Test not auth user can follow."""
        count_before = Follow.objects.filter(
            user=self.follower, author=self.author).count()
        self.client.get(
            reverse('posts:profile_follow', args=(self.author.username,))
        )
        self.assertEqual(
            Follow.objects.filter(
                user=self.follower, author=self.author).count(),
            count_before
        )

    def test_remove_follow(self):
        """Test auth user can unfollow."""
        author_test = User.objects.create(username='Author_test')
        count_before = Follow.objects.filter(
            user=self.follower, author=author_test).count()
        Follow.objects.create(
            author=author_test, user=self.follower)
        self.assertEqual(
            Follow.objects.filter(
                user=self.follower, author=author_test).count(),
            count_before + 1
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                args=(author_test.username,)
            )
        )
        self.assertEqual(Follow.objects.filter(
            user=self.follower, author=author_test).count(), count_before)

    def test_show_author_post_on_follower_page(self):
        """Test show author post on follower_page"""
        Follow.objects.create(user=self.follower, author=self.author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        last_post = response.context['page_obj']
        self.assertIn(self.post, last_post)

    def test_not_show_author_post_on_not_follower_page(self):
        """Test not show author post on not follower_page."""
        other_follower = User.objects.create(username='other_follower')
        post_test = Post.objects.create(
            author=other_follower,
            text='test_text'
        )
        new_client = Client()
        new_client.force_login(other_follower)
        response = new_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post_test, response.context['page_obj'])

    def test_user_not_follow_yourself(self):
        """Test user not follow yourself."""
        count_before = Follow.objects.filter(
            user=self.follower, author=self.follower).count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.follower.username,)
            )
        )
        self.assertEqual(
            Follow.objects.filter(
                user=self.follower, author=self.follower).count(),
            count_before
        )
