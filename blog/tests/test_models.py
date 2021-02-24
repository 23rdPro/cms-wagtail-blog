from blog.models import AlternateTemplateMixin, Blog, BlogCategory, About, Tag
from home.models import HomePage
from django.core.management.color import no_style
from django.db import connections, connection
from django.db.models.base import ModelBase
from django.test import TestCase
from django.db.utils import ProgrammingError
from wagtail.core.models import Site
from wagtail.core.models import Page
from django.contrib.contenttypes.models import ContentType
from django.db.models import ImageField
# testing abstract model
from wagtail.tests.utils import WagtailPageTests
from django.core.files.uploadedfile import SimpleUploadedFile


# reference
from wagtail.tests.utils.form_data import nested_form_data, streamfield


class ModelMixinTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'model'):
            cls.model = ModelBase('AlternateTemplateMixin', (AlternateTemplateMixin,),
                                  {'__module__': AlternateTemplateMixin.__module__})
            # cls.tag_model = ModelBase('Tag', (Tag,), {'__module__': Tag.__module__})
        # cls.model = ModelBase('__TestModel__' + cls.mixin.__name__,
        #                       (cls.mixin,), {'__module__': cls.mixin.__module__})
        # super(ModelMixinTestCase, cls).setUpClass()

        # schema creation
        else:
            try:
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(cls.model)
                    # schema_editor.create_model(cls.tag_model)
                super(ModelMixinTestCase, cls).setUpClass()
            except ProgrammingError:
                pass
            # cls._test_base = cls.tag_model.objects.create()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'model'):
            try:
                with connection.schema_editor() as schema_editor:
                    schema_editor.delete_model(cls.model)
                    # schema_editor.delete_model(cls.tag_model)
                super(ModelMixinTestCase, cls).tearDownClass()
            except ProgrammingError:
                pass


class TestBlogTree(WagtailPageTests, ModelMixinTestCase):
    # mixin = Tag

    def setUp(self):
        root = Page.get_first_root_node()
        homepage_content_type = ContentType.objects.get_for_model(HomePage)
        homepage = HomePage(
            title='Test title',
            slug='test-title',
            show_in_menus=True,
            content_type=homepage_content_type
        )
        root.add_child(instance=homepage)

        parent_page = HomePage.objects.first()
        blog_content_type = ContentType.objects.get_for_model(Blog)
        about_content_type = ContentType.objects.get_for_model(About)

        blog = Blog(
            title='Blog title',
            slug='blog-title',
            show_in_menus=True,
            content_type=blog_content_type,
            alternate_template='Alternate Template Test',
            experiment_slug='alternate-test',
            tags=['test', 'python']
        )

        about = About(
            title='About',
            slug='about',
            show_in_menus=True,
            content_type=about_content_type,
            resume='http://localhost:8000',
            text='This is admin',
            image=SimpleUploadedFile(
                name="pexels-photo-1005644.original.jpg",
                content=open("media/images/pexels-photo-1005644.original.jpg", 'rb').read(),
                content_type='image/jpeg'
            )
        )

        # parent_page.add_child(instance=about)
        parent_page.add_child(instance=blog)
        root.add_child(instance=about)

        BlogCategory.objects.create(
            name='Test',
            slug='test'
        )

    def test_blog_pages(self):
        root = Page.get_first_root_node().get_children().count()
        self.assertEqual(root, 3)  # Home, About, Blog = 3
        instance_blog = Blog.objects.get(slug='blog-title')
        instance_about = About.objects.get(slug='about')
        instance_homepage = HomePage.objects.get(slug='test-title')
        count_blog = Blog.objects.all().count()
        count_homepage = HomePage.objects.all().count()
        self.assertEqual(count_homepage, 2)
        self.assertTrue(instance_about)
        self.assertTrue(instance_homepage)
        self.assertTrue(instance_blog)
        self.assertEqual(count_blog, 1)
        self.assertTrue(instance_blog.tags)
        # self.assertEqual(count_homepage, 1) the homepage gets added to,its a tree
        self.assertGreater(count_homepage, count_blog)

        instance_blog_category = BlogCategory.objects.get(pk=1)
        self.assertIsInstance(instance_blog_category, BlogCategory)
        max_length = instance_blog_category._meta.get_field('name').max_length
        self.assertEqual(max_length, 32)
        slug = instance_blog_category._meta.get_field('slug').unique
        self.assertTrue(slug)

    def wagtail_specific_test(self):
        instance_root = Page.get_first_root_node()
        self.assertCanCreateAt(HomePage, Blog)
        self.assertCanCreateAt(HomePage, About)
        self.assertCanNotCreateAt(HomePage, BlogCategory)
        self.assertCanCreateAt(instance_root, HomePage)
        self.assertCanNotCreateAt(Blog, AlternateTemplateMixin)
        self.assertCanCreate(instance_root, HomePage, nested_form_data({
            'title': 'Title Homepage',
            'slug': 'title-homepage'
        }))
        self.assertCanCreate(HomePage, Blog, nested_form_data({
            'title': 'Blog title',
            'date': "2023-3-3 01:01:00.000000-08:00",
            'slug': 'test-title',
            'body': streamfield([
                ('text', 'another section containing text'),
                ('text 2', 'yet another section containing code'),
            ])
        }))
        self.assertCanCreate((HomePage, About, nested_form_data({
            'title': 'About',
            'slug': 'about',
            'text': 'This is admin',
            'resume': 'http://localhost:8000',
            'image': SimpleUploadedFile(
                name="pexels-photo-1005644.original.jpg",
                content=open("media/images/pexels-photo-1005644.original.jpg", 'rb').read(),
                content_type='image/jpeg'
            )

        })))


class TestTagModel(TestCase):
    def setUp(self) -> None:
        Tag.objects.create(name='python', slug='python')

    def test_instance(self):
        instance = Tag.objects.get(id=1)
        self.assertTrue(isinstance(instance, Tag))

