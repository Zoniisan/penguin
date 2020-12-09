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
    path(
        'staff/theme_slack',
        views.staff.ThemeSlackView.as_view(),
        name='staff_theme_slack'
    ),
    path(
        'staff/theme_slack/delete',
        views.staff.ThemeSlackDeleteView.as_view(),
        name='staff_theme_slack_delete'
    ),

    # views/submit.py
    path(
        'submit',
        views.submit.SubmitView.as_view(),
        name='submit_submit'
    ),
    path(
        'submit/staff',
        views.submit.StaffSubmitView.as_view(),
        name='submit_staff_submit'
    ),
    path(
        'submit/schedule',
        views.submit.ScheduleView.as_view(),
        name='submit_schedule'
    ),
    path(
        'submit/schedule/delete',
        views.submit.ScheduleDeleteView.as_view(),
        name='submit_schedule_delete'
    ),
    path(
        'submit/list',
        views.submit.ListView.as_view(),
        name='submit_list'
    ),
    path(
        'submit/update/<slug:pk>',
        views.submit.UpdateView.as_view(),
        name='submit_update'
    ),
    path(
        'submit/delete/<slug:pk>',
        views.submit.DeleteView.as_view(),
        name='submit_delete'
    ),
]
