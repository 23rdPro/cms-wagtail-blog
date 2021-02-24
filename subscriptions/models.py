from django.db import models
from django.conf import settings
from django.db.models import Manager
from sendgrid import SendGridAPIClient
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, PageManager
from wagtail.core.signals import page_published
from wagtail.search import index
from wagtailmarkdown.blocks import MarkdownBlock
from sendgrid.helpers.mail import Mail


exposed_request = None  # request middleware


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    conf_num = models.CharField(max_length=179)
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email

    objects = Manager()


class Newsletter(Page):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contents = StreamField([
        ('body', MarkdownBlock())
    ])

    # subject = models.CharField(max_length=512)

    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = "Newsletters"

    search_fields = Page.search_fields + [
        index.SearchField('title', partial_match=True),
        index.SearchField('contents'),

    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel("contents"),
        # FieldPanel("subject"),

    ]

    objects = PageManager()

    def send_email(self, request):
        subscribers = Subscriber.objects.filter(confirmed=True)
        server = SendGridAPIClient(settings.SENDGRID_API_KEY)

        for subscriber in subscribers:
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=subscriber.email,
                subject=self.title,
                html_content=str(self.contents) +
                '<br><a href="%s/unsubscribe/?email=%s&conf_num=%s">Unsubscribe</a>.' % (request.build_absolute_uri(
                    'http://localhost:8000'), subscriber.email, subscriber.conf_num)
            )  # TODO: change uri from localhost when you pay for domain
            server.send(message)


# wagtail signal calls model's send method on specific queryset
# to avoid sending same letter twice, newsletter will only be published once
# although if there's an edit it can be republished at which point it will be sent again to confirmed subscribers
def receiver(sender, **kwargs):
    queryset = Newsletter.objects.all()

    for newsletter in queryset:
        if newsletter == kwargs["instance"]:
            newsletter.send_email(exposed_request)


page_published.connect(receiver, sender=Newsletter)
