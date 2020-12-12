from django.contrib import admin

from theme import models


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('基本情報', {
            'fields': (
                'theme', 'description', 'writer', 'create_datetime'
            )
        }),
        ('強制提出', {
            'fields': (
                'submit_staff',
            )
        }),
        ('編集', {
            'fields': (
                'update_staff', 'update_datetime'
            )
        }),
    )

    readonly_fields = (
        'create_datetime', 'update_datetime'
    )

    autocomplete_fields = (
        'writer', 'submit_staff', 'update_staff'
    )

    list_display = (
        'theme', 'writer', 'create_datetime'
    )

    search_fields = (
        'theme',
    )


@admin.register(models.SubmitSchedule)
class SubmitScheduleAdmin(admin.ModelAdmin):
    fields = (
        'start_datetime', 'finish_datetime'
    )

    list_display = (
        'start_datetime', 'finish_datetime'
    )


@admin.register(models.VoteSchedule)
class VoteScheduleAdmin(admin.ModelAdmin):
    fieldsets = (
        ('基本情報', {
            'fields': (
                'name', 'description', 'start_datetime', 'finish_datetime'
            )
        }),
        ('候補', {
            'fields': (
                'theme_list',
            )
        }),
    )

    filter_horizontal = (
        'theme_list',
    )

    list_display = (
        'name', 'start_datetime', 'finish_datetime'
    )

    search_fields = (
        'name',
    )


@admin.register(models.Vote)
class VoteAdmin(admin.ModelAdmin):
    fields = (
        'schedule', 'theme', 'create_datetime'
    )

    autocomplete_fields = (
        'schedule', 'theme'
    )

    readonly_fields = (
        'create_datetime',
    )

    list_display = (
        'schedule', 'theme', 'create_datetime'
    )


@admin.register(models.Eptid)
class EptidAdmin(admin.ModelAdmin):
    fields = (
        'schedule', 'eptid'
    )

    autocomplete_fields = (
        'schedule',
    )

    list_display = (
        'schedule', 'eptid'
    )

    search_fields = (
        'eptid',
    )


@admin.register(models.ThemeStaff)
class ThemeStaffAdmin(admin.ModelAdmin):
    fields = (
        'user',
    )

    autocomplete_fields = (
        'user',
    )

    list_display = (
        'user',
    )


@admin.register(models.ThemeSlack)
class ThemeSlackAdmin(admin.ModelAdmin):
    fields = (
        'slack_ch',
    )

    list_display = (
        'slack_ch',
    )
