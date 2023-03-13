from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    """Post model testing"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Test model Post have correct object name."""
        self.assertEqual(
            str(PostModelTest.post),
            PostModelTest.post.text[:15]
        )

    def test_models_have_verbose_name(self):
        """Test verbose_name."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_models_have_help_text(self):
        """Test help_text."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Укажите название вашей группы'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    """Group model testing."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа поклонников графа',
            slug='tolstoi',
            description='Что-то о группе'
        )

    def test_models_have_correct_object_names(self):
        """Test model Group have correct object name."""
        group = GroupModelTest.group
        self.assertEqual(str(group), group.title)
