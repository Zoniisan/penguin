from django.contrib import admin
from project import models


@admin.register(models.Kind)
class KindAdmin(admin.ModelAdmin):
    fields = (
        'name', 'symbol', 'food', 'staff_list', 'slack_ch'
    )

    autocomplete_fields = (
        'staff_list',
    )

    list_display = (
        'name', 'symbol', 'food', 'slack_ch'
    )

    search_fields = (
        'name',
    )
