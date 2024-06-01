"""
URL configuration for Server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from api.views import RegisterView, LoginView, RegenerateAccessTokenView, GetProfile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register', RegisterView.as_view(), name='register'),
    path('user/login', LoginView.as_view(), name='login'),
    path('user/regenerate_token', RegenerateAccessTokenView.as_view(), name='regenerate-tokken'),
    path('user/get_profile/', GetProfile.as_view(), name='get_profile'),
    path('assignment/', include('api.urls'))
]
