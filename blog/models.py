from datetime import datetime
from django.db import models
from django import forms
from django.db.models import Count

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from users.models import User
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailmarkdown.blocks import MarkdownBlock
from taggit.models import Tag as BlogTag, TaggedItemBase

# AB testing to measure conversion rate by page <abstract:True>
from wagtailseo.models import SeoMixin, SeoType, TwitterCard


class AlternateTemplateMixin(models.Model):
    alternate_template = models.CharField(max_length=100, blank=True)
    experiment_slug = models.CharField(max_length=50, blank=True)

    settings_panels = [
        FieldPanel('alternate_template'),
        FieldPanel('experiment_slug'),

    ]

    class Meta:
        abstract = True

    def get_template(self, request, *args, **kwargs):
        if self.alternate_template:
            return self.alternate_template
        else:
            return super(AlternateTemplateMixin, self).get_template(request)


class Blog(SeoMixin, AlternateTemplateMixin, Page):
    # owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(verbose_name='Post date', default=datetime.today)
    updated = models.DateTimeField(auto_now=True)
    body = StreamField([
        ('body', MarkdownBlock()),
        ('code', MarkdownBlock()),
        ('image', MarkdownBlock()),
        ('toc', MarkdownBlock()),
    ])
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)

    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE
    promote_panels = SeoMixin.seo_panels
    # seo_title = ""
    # search_description = ""

    # def seo_author(self) -> str:
    #     return str(self.author)

    search_fields = Page.search_fields + [
        index.SearchField('title', partial_match=True, boost=2),
        index.SearchField('tags'),
        index.SearchField('body'),
        index.FilterField('date'),
        index.RelatedFields('categories', [
            index.FilterField('name'),
        ])
    ]

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
        FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
        InlinePanel('gallery_images', label='gallery images'),

    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('date'),

    ]

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    @property
    def blog_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(Blog, self).get_context(request, *args, **kwargs)
        context['blog_page'] = self.blog_page
        context['post'] = self
        context['experiment_slug'] = self.experiment_slug
        context['tags'] = Tag.objects.all()
        context['menuitems'] = self.get_children().filter(
            live=True, show_in_menus=True
        )
        context['categories'] = BlogCategory.objects.annotate(blogs=Count('blog'))
        return context


class BlogGalleryImages(Orderable):  # SeoMixin
    page = ParentalKey(Blog, on_delete=models.SET_NULL, null=True, related_name='gallery_images')
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL, null=True, related_name='+')
    caption = models.CharField(max_length=49)
    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),

    ]
    # seo_description_sources = [
    #     'serach_description',
    #     'caption',
    # ]
    #
    # seo_image_sources = [
    #     'og_image',
    #     'image',
    # ]


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True, max_length=64)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),

    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('Blog', related_name='post_tags', on_delete=models.CASCADE)


@register_snippet
class Tag(BlogTag):
    class Meta:
        proxy = True


class About(Page):
    text = RichTextField(max_length=400)
    resume = models.URLField(max_length=299)
    image = models.ImageField(upload_to='admin_images/')

    content_panels = Page.content_panels + [
        FieldPanel("text"),
        FieldPanel("resume"),
        FieldPanel("image")
    ]

    search_fields = Page.search_fields + [
        index.SearchField('text')
    ]
