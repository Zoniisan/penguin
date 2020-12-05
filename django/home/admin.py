from django.contrib import admin
from django.contrib.auth.models import Group
from home import models

# Permission Group は使用しないので削除
admin.site.unregister(Group)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('基本情報', {
            'fields': (
                'last_name', 'first_name', 'last_name_kana', 'first_name_kana',
                'stid', 'faculty', 'grade'
            )
        }),
        ('連絡先', {
            'fields': (
                'email', 'tel'
            )
        }),
        ('権限情報', {
            'fields': (
                'is_active', 'is_admin'
            )
        }),
        ('Shibboleth 情報', {
            'classes': ('collapse',),
            'fields': ('eptid', 'affiliation'),
        }),
    )

    list_display = (
        'stid', 'last_name', 'first_name', 'last_name_kana', 'first_name_kana',
        'is_staff', 'is_admin'
    )

    search_fields = (
        'stid', 'last_name', 'first_name', 'last_name_kana', 'first_name_kana',
        'email'
    )


@admin.register(models.IdentifyToken)
class IdentifyTokenAdmin(admin.ModelAdmin):
    fields = (
        'eptid', 'email', 'create_datetime', 'is_used'
    )

    readonly_fields = (
        'create_datetime',
    )

    list_display = (
        'email', 'create_datetime', 'is_used'
    )

    list_filter = (
        'is_used',
    )

    search_fields = (
        'email',
    )


@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    fields = (
        'name', 'member', 'email', 'slack_ch'
    )

    autocomplete_fields = (
        'member',
    )

    list_display = (
        'name', 'email', 'slack_ch'
    )

    search_fields = (
        'name',
    )


@admin.register(models.Notice)
class NoticeAdmin(admin.ModelAdmin):
    fields = (
        'subject', 'body', 'writer',
        'start_datetime', 'finish_datetime'
    )

    autocomplete_fields = (
        'writer',
    )

    list_display = (
        'subject', 'writer', 'start_datetime', 'finish_datetime'
    )

    search_fields = (
        'subject', 'body'
    )


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    fields = (
        'subject', 'body', 'writer',
        'to', 'department', 'create_datetime'
    )

    readonly_fields = (
        'create_datetime',
    )

    autocomplete_fields = (
        'writer', 'to'
    )

    list_display = (
        'subject', 'writer', 'department', 'create_datetime'
    )

    search_fields = (
        'subject', 'body'
    )


@admin.register(models.MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    fields = (
        'message', 'user', 'create_datetime'
    )

    readonly_fields = (
        'create_datetime',
    )

    autocomplete_fields = (
        'message', 'user'
    )

    list_display = (
        'message', 'user', 'create_datetime'
    )


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    fields = (
        'kind', 'body', 'writer', 'create_datetime',
        'is_finished', 'message'
    )

    readonly_fields = (
        'create_datetime',
    )

    autocomplete_fields = (
        'writer', 'message'
    )

    list_display = (
        'kind', 'writer', 'create_datetime', 'is_finished'
    )

    list_filter = (
        'is_finished',
    )

    search_fields = (
        'body',
    )


@admin.register(models.ContactKind)
class ContactKindAdmin(admin.ModelAdmin):
    fields = (
        'name', 'department'
    )

    autocomplete_fields = (
        'department',
    )

    list_display = (
        'name',
    )
