from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from home import views

app_name = 'home'

urlpatterns = [
    # views/auth.py
    path(
        'auth/profile',
        views.auth.ProfileView.as_view(),
        name='auth_profile'
    ),
    path(
        'auth/identify_token/create',
        views.auth.IdentifyTokenCreateView.as_view(),
        name='auth_identify_token_create'
    ),
    path(
        'auth/identify_token/success',
        views.auth.IdentifyTokenSuccessView.as_view(),
        name='auth_identify_token_success'
    ),
    path(
        'auth/identify/<slug:token_id>',
        views.auth.IdentifyView.as_view(),
        name='auth_identify'
    ),
    path(
        'auth/user/list',
        views.auth.UserListView.as_view(),
        name='auth_user_list'
    ),
    path(
        'auth/user/detail/<slug:pk>',
        views.auth.UserDetailView.as_view(),
        name='auth_user_detail'
    ),
    path(
        'auth/user/update/<slug:pk>',
        views.auth.UserUpdateView.as_view(),
        name='auth_user_update'
    ),
    path(
        'auth/user/delete/<slug:pk>',
        views.auth.UserDeleteView.as_view(),
        name='auth_user_delete'
    ),
    path(
        'auth/login',
        views.auth.LoginView.as_view(),
        name='auth_login'
    ),
    path(
        'auth/logout',
        views.auth.LogoutView.as_view(),
        name='auth_logout'
    ),

    # view/contact.py
    path(
        'contact/create',
        views.contact.CreateView.as_view(),
        name='contact_create'
    ),
    path(
        'contact/list',
        views.contact.ListView.as_view(),
        name='contact_list'
    ),
    path(
        'contact/detail/<slug:pk>',
        views.contact.DetailView.as_view(),
        name='contact_detail'
    ),
    path(
        'contact/finish/<slug:pk>',
        views.contact.FinishView.as_view(),
        name='contact_finish'
    ),

    # views/contactkind.py
    path(
        'contactkind/list',
        views.contactkind.ListView.as_view(),
        name='contactkind_list'
    ),
    path(
        'contactkind/create',
        views.contactkind.CreateView.as_view(),
        name='contactkind_create'
    ),
    path(
        'contactkind/update/<slug:pk>',
        views.contactkind.UpdateView.as_view(),
        name='contactkind_update'
    ),
    path(
        'contactkind/delete/<slug:pk>',
        views.contactkind.DeleteView.as_view(),
        name='contactkind_delete'
    ),

    # views/department.py
    path(
        'department/list',
        views.department.ListView.as_view(),
        name='department_list'
    ),
    path(
        'department/create',
        views.department.CreateView.as_view(),
        name='department_create'
    ),
    path(
        'department/update/<slug:pk>',
        views.department.UpdateView.as_view(),
        name='department_update'
    ),
    path(
        'department/delete/<slug:pk>',
        views.department.DeleteView.as_view(),
        name='department_delete'
    ),
    path(
        'department/admin',
        views.department.AdminView.as_view(),
        name='department_admin'
    ),

    # view/message.py
    path(
        'message/list',
        views.message.ListView.as_view(),
        name='message_list'
    ),
    path(
        'message/detail/<slug:pk>',
        views.message.DetailView.as_view(),
        name='message_detail'
    ),
    path(
        'message/staff_list',
        views.message.StaffListView.as_view(),
        name='message_staff_list'
    ),
    path(
        'message/staff_create/<slug:mode>',
        views.message.StaffCreateView.as_view(),
        name='message_create'
    ),
    path(
        'message/staff_create/<slug:mode>/<slug:arg>',
        views.message.StaffCreateView.as_view(),
        name='message_create'
    ),
    path(
        'message/staff_detail/<slug:pk>',
        views.message.StaffDetailView.as_view(),
        name='message_staff_detail'
    ),
    path(
        'message/staff_readlist/<slug:pk>',
        views.message.StaffReadListView.as_view(),
        name='message_staff_readlist'
    ),

    # views/notice.py
    path(
        'notice/list',
        views.notice.ListView.as_view(),
        name='notice_list'
    ),
    path(
        'notice/create',
        views.notice.CreateView.as_view(),
        name='notice_create'
    ),
    path(
        'notice/update/<slug:pk>',
        views.notice.UpdateView.as_view(),
        name='notice_update'
    ),
    path(
        'notice/delete/<slug:pk>',
        views.notice.DeleteView.as_view(),
        name='notice_delete'
    ),

    # views/root.py
    path(
        '',
        views.root.IndexView.as_view(),
        name='index'
    ),

    # views/staff.py
    path(
        'staff/menu',
        views.staff.MenuView.as_view(),
        name='staff_menu'
    ),
    path(
        'staff/member',
        views.staff.MemberView.as_view(),
        name='staff_member'
    ),
    path(
        'staff/download_vcf/<slug:mode>',
        views.staff.DownloadVcfView.as_view(),
        name='staff_download_vcf'
    ),
]

# Django REST framework
# djangorestframework-datatables で使用
# https://pypi.org/project/djangorestframework-datatables/
router = routers.DefaultRouter()
router.register('user', views.UserViewSet)

urlpatterns += [
    url('^api/', include(router.urls)),
]
