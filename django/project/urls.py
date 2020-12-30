from django.urls import path

from project import views

app_name = 'project'

urlpatterns = [
    # views/kind.py
    path(
        'kind/list',
        views.kind.ListView.as_view(),
        name='kind_list'
    ),
    path(
        'kind/create',
        views.kind.CreateView.as_view(),
        name='kind_create'
    ),
    path(
        'kind/update/<slug:pk>',
        views.kind.UpdateView.as_view(),
        name='kind_update'
    ),
    path(
        'kind/delete/<slug:pk>',
        views.kind.DeleteView.as_view(),
        name='kind_delete'
    ),
]
