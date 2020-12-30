from django.urls import path

from register import views

app_name = 'register'

urlpatterns = [
    # views/root.py
    path(
        'verify/<slug:token>',
        views.root.VerifyView.as_view(),
        name='verify'
    ),
    path(
        'create',
        views.root.CreateView.as_view(),
        name='create'
    ),
    # views/staff.py
    path(
        'staff/menu',
        views.staff.MenuView.as_view(),
        name='staff_menu'
    ),
    path(
        'staff/signage',
        views.staff.SignageView.as_view(),
        name='staff_signage'
    ),
]
