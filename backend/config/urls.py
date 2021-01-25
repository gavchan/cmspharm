"""config URL Configuration

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
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('cms-admin/', admin.site.urls),
    path('cms-auth/', include('django.contrib.auth.urls')),
    path('cmsacc/', include('cmsacc.urls')),
    path('cmsinv/', include('cmsinv.urls')),
    path('cmssys/', include('cmssys.urls')),
    path('drugdb/', include('drugdb.urls')),
    path('inventory/', include('inventory.urls')),
    path('ledger/', include('ledger.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.HomeSelectVendorView, name='home'),
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
