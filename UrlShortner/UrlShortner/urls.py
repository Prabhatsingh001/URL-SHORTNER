"""
URL configuration for UrlShortner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from Auth.views import IndexView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = "urlLogic.views.F404_page"

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", IndexView.as_view(), name="index"),
    path("accounts/", include(("Auth.urls", "Auth"), namespace="accounts")),
    path("url/", include(("urlLogic.urls", "urlLogic"), namespace="url")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
