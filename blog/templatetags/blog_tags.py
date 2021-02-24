from six.moves.urllib.parse import urlparse, urlunparse
from django import template

register = template.Library()


@register.simple_tag()
def post_date_url(post, blog_page):
    post_date = post.date
    post_url = blog_page.url + blog_page.reverse_subpage(
        'post_by_date_slug',
        args=(
            post_date.year,
            '{0:02}'.format(post_date.month),
            '{0:02}'.format(post_date.day),
            post.slug,
        )
    )
    return post_url


@register.inclusion_tag('blog/disqus.html', takes_context=True)
def show_comments(context):
    blog_page = context['blog_page']
    post = context['post']
    path = post_date_url(post, blog_page)

    raw_url = context['request'].get_raw_uri()
    parse_result = urlparse(raw_url)
    abs_path = urlunparse([
        parse_result.scheme,
        parse_result.netloc,
        path,
        "",
        "",
        "",
    ])
    return {'disqus_url': abs_path,
            'disqus_identifier': post.pk,
            'request': context['request']
            }
