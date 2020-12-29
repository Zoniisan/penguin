"""penguin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # penguin
    path('', include('home.urls')),
    path('theme/', include('theme.urls')),

    # admin
    path('admin/', admin.site.urls),

    # third party
    path("select2/", include('django_select2.urls')),
]

# debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Admin Site Settings
admin.site.site_title = '管理サイト | PENGUIN'
admin.site.site_header = 'PENGUIN 管理サイト'
admin.site.index_title = 'メニュー'
