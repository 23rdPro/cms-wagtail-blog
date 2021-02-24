from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Subscriber, Newsletter


class SubscriptionAdmin(ModelAdmin):
    model = Subscriber
    menu_icon = 'mail'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        'email',
        'conf_num',
        'confirmed'
    )
    list_filter = 'confirmed',
    search_fields = 'email', 'confirmed'
    list_export = 'email',  # when exporting field


modeladmin_register(SubscriptionAdmin)


class NewsletterAdmin(ModelAdmin):
    model = Newsletter
    menu_icon = 'mail'
    menu_order = 300
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        'created_at',
        'updated_at',
        'contents',
    )
    list_filter = 'created_at', 'updated_at'
    search_fields = 'contents',


modeladmin_register(NewsletterAdmin)