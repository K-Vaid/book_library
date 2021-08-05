"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView

from django.conf import settings
from django.conf.urls.static import static

from catalog.forms import CustomAuthForm


urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('catalog/', include("catalog.urls")),
    path('catalog/reviews/', include("reviews.urls")),
    path("", RedirectView.as_view(url='catalog/', permanent=True)),
    path("accounts/login/", LoginView.as_view(
                                        redirect_authenticated_user=True,
                                        form_class = CustomAuthForm
                                    ), name="login"),
    path("accounts/", include('django.contrib.auth.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_title = "Library"
admin.site.site_header = "Local Library"
admin.site.index_title = "Admin Panel"