from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views import defaults as default_views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from subscriptions.views import subscribe, confirm, unsubscribe

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.search, name='search'),
    re_path(r'^robots\.txt', include('robots.urls')),

    # subscriptions app
    path('subscribe/', subscribe, name='subscribe'),
    path('confirm-subscription/', confirm, name='confirm'),
    path('unsubscribe/', unsubscribe, name='delete'),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        # TODO: customize html following text/404.html etc
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
        re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
        re_path(r'^500/$', default_views.server_error),
        re_path(r'^400/$', default_views.bad_request, kwargs={'exception': Exception}),
        re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception})
    ] + urlpatterns

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
