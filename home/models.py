import datetime
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Count
from django.http import Http404
from django.utils.dateformat import DateFormat
from django.utils.formats import date_format
from users.models import User
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page
from wagtailseo.models import SeoMixin, SeoType, TwitterCard

from blog.models import AlternateTemplateMixin, About, Tag, BlogCategory, Blog


class HomePage(SeoMixin, AlternateTemplateMixin, RoutablePageMixin, Page):
    # tautology
    # owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_panels = Page.content_panels + []
    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE
    promote_panels = SeoMixin.seo_panels
    # search_description = "Articles listing page- Olumide Bakare"
    # seo_title = ""

    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)
        posts = self.get_posts()
        # about = About.objects.all()[0]
        paginator = Paginator(posts, 10)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)  # empty page

        context['posts'] = posts
        # context['about'] = about
        context['blog_page'] = self
        context['menuitems'] = self.get_children().filter(live=True, show_in_menus=True)
        context['experiment_slug'] = self.experiment_slug
        context['tags'] = Tag.objects.all()
        context['categories'] = BlogCategory.objects.annotate(blogs=Count('blog'))
        return context

    def get_posts(self):
        return Blog.objects.descendant_of(self).live().order_by('-date')

    def get_latest(self):
        return Blog.objects.descendant_of(self).live().all().reverse()[0]

    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def post_by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_posts().filter(date__year=year)
        if month:
            self.posts = self.posts.filter(date__month=month)
            d_format = DateFormat(datetime.date(int(year), int(month), int(day)))
            self.search_term = d_format.format('F Y')
        if day:
            self.posts = self.posts.filter(date__day=day)
            self.search_term = date_format(datetime.date(int(year), int(month), int(day)))
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/(\d{2})/(\d{2})/(.+)/$')
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        post_page = self.get_posts().filter(slug=slug).first()
        # post_page = self.get_posts().filter(slug=slug)[0]
        if not post_page:
            raise Http404
        return Page.serve(post_page, request, *args, **kwargs)

    # TODO: post_by_tag is not getting any request so no filter actually happens
    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.search_type = 'tag'
        self.search_term = tag
        self.posts = Blog.objects.live().filter(tags__slug='python')
        return Page.serve(self, request, *args, *kwargs)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.posts = self.get_posts().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)
