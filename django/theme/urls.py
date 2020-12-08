from django.urls import path

from theme import views

app_name = 'theme'

urlpatterns = [
    # views/staff.py
    path(
        'staff/menu',
        views.staff.MenuView.as_view(),
        name='staff_menu'
    ),
    path(
        'staff/theme_staff',
        views.staff.ThemeStaffView.as_view(),
        name='staff_theme_staff'
    ),
]
