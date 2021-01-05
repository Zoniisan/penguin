from django.contrib import admin
from register import models


@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('基本情報', {
            'fields': (
                'verbose_id', 'temp_leader', 'kind', 'food',
                'group', 'group_kana', 'note'
            )
        }),
        ('状態', {
            'fields': (
                'status', 'call_id'
            )
        }),
        ('履歴', {
            'fields': (
                'create_datetime', 'finish_datetime', 'finish_staff'
            )
        }),
        ('企画責任者確定', {
            'fields': (
                'leader_token',
            )
        }),
    )

    readonly_fields = (
        'create_datetime', 'leader_token'
    )

    autocomplete_fields = (
        'temp_leader', 'finish_staff'
    )

    list_display = (
        'group', 'kind', 'food', 'temp_leader', 'status', 'verbose_id'
    )

    search_fields = (
        'group', 'group_kana', 'verbose_id',
        'temp_leader__last_name', 'temp_leader__first_name',
        'temp_leader__last_name_kana', 'temp_leader__first_name_kana',
    )

    list_filter = (
        'kind', 'food', 'status'
    )


@admin.register(models.Window)
class WindowAdmin(admin.ModelAdmin):
    fields = (
        'name', 'kind_list', 'staff', 'registration'
    )

    autocomplete_fields = (
        'staff', 'registration'
    )

    filter_horizontal = (
        'kind_list',
    )

    list_display = (
        'name', 'staff'
    )

    search_fields = (
        'name',
    )


@admin.register(models.VerifyToken)
class VerifyTokenAdmin(admin.ModelAdmin):
    fields = (
        'id', 'create_datetime'
    )

    readonly_fields = (
        'id', 'create_datetime'
    )


@admin.register(models.VerifiedUser)
class VerifiedUserAdmin(admin.ModelAdmin):
    fields = (
        'user', 'create_datetime'
    )

    readonly_fields = (
        'create_datetime',
    )

    autocomplete_fields = (
        'user',
    )

    list_display = (
        'user', 'create_datetime'
    )

    search_fields = (
        'user__last_name', 'user__first_name',
        'user__last_name_kana', 'user__first_name_kana',
    )


@admin.register(models.RegisterStaff)
class RegisterStaffAdmin(admin.ModelAdmin):
    fields = (
        'user',
    )

    autocomplete_fields = (
        'user',
    )

    list_display = (
        'user',
    )

    search_fields = (
        'user__last_name', 'user__first_name',
        'user__last_name_kana', 'user__first_name_kana',
    )
