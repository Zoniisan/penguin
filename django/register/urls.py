
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
    path(
        'success/<slug:pk>',
        views.root.SuccessView.as_view(),
        name='success'
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
    path(
        'staff/window_open',
        views.staff.WindowOpenView.as_view(),
        name='staff_window_open'
    ),
    path(
        'staff/window/<slug:window_pk>',
        views.staff.WindowView.as_view(),
        name='staff_window'
    ),
    path(
        'staff/window/<slug:window_pk>/<slug:pk>',
        views.staff.WindowUpdateView.as_view(),
        name='staff_window_update'
    ),
    path(
        'staff/window_close/<slug:pk>',
        views.staff.WindowCloseView.as_view(),
        name='staff_window_close'
    ),
    path(
        'staff/admin/list',
        views.staff.AdminListView.as_view(),
        name='staff_admin_list'
    ),
    path(
        'staff/admin/detail/<slug:pk>',
        views.staff.AdminDetailView.as_view(),
        name='staff_admin_detail'
    ),
    path(
        'staff/admin/live',
        views.staff.AdminLiveView.as_view(),
        name='staff_admin_live'
    ),
]
