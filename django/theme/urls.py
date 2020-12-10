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

    # views/vote.py
    path(
        'vote/<slug:pk>',
        views.vote.VoteView.as_view(),
        name='vote'
    ),
    path(
        'vote/create/<slug:vote_schedule_id>/<slug:theme_id>',
        views.vote.VoteCreateView.as_view(),
        name='vote_create'
    ),
    path(
        'vote/schedule/create',
        views.vote.ScheduleCreateView.as_view(),
        name='vote_schedule_create'
    ),
    path(
        'vote/schedule/update/<slug:pk>',
        views.vote.ScheduleUpdateView.as_view(),
        name='vote_schedule_update'
    ),
    path(
        'vote/schedule/delete/<slug:pk>',
        views.vote.ScheduleDeleteView.as_view(),
        name='vote_schedule_delete'
    ),
    path(
        'vote/list/pending/<slug:vote_schedule_id>',
        views.vote.ListPendingView.as_view(),
        name='vote_list_pending'
    ),
    path(
        'vote/list/pending/<slug:vote_schedule_id>'
        '/<slug:result_vote_schedule_id>',
        views.vote.ListPendingView.as_view(),
        name='vote_list_pending'
    ),
    path(
        'vote/result/<slug:vote_schedule_id>',
        views.vote.ResultView.as_view(),
        name='vote_result'
    ),
]
