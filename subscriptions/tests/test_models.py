from django.test import TestCase
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, streamfield

from home.models import HomePage
from blog.models import Blog, About

from ..models import Subscriber, Newsletter
from ..views import random_digits


class SubscriberTest(TestCase):
    def setUp(self) -> None:
        Subscriber.objects.create(
            email='mailadmin@admin.com',
            conf_num=random_digits(),
        )

        Subscriber.objects.create(
            email='adminmail@admin.com',
            conf_num=random_digits(),
            confirmed=True
        )

    def test_random_digits(self):
        first_user = Subscriber.objects.get(id=1)
        second_user = Subscriber.objects.get(id=2)
        self.assertNotEqual(first_user.conf_num, second_user.conf_num)
        self.assertTrue(second_user.confirmed)
        self.assertFalse(first_user.confirmed)


class TestPageCanCreateAt(WagtailPageTests):
    def test_can_create_at(self):
        self.assertCanCreateAt(HomePage, Newsletter)
        self.assertCanNotCreateAt(HomePage, Subscriber)
        self.assertAllowedParentPageTypes(
            Newsletter, set([Page, HomePage, Newsletter, Blog, About])  # python 3 literal for set
        )
        self.assertAllowedSubpageTypes(Newsletter, set([Page, HomePage, Newsletter, Blog, About]))

    def can_create_content_page(self):
        root = HomePage.objects.get(pk=2)
        self.assertCanCreate(root, Newsletter, nested_form_data({
            'title': 'Django REST Framework',
            'subject': 'Django REST Framework',
            'contents': streamfield([
                ('text', 'Using graphene with django'),
            ])
        }))
