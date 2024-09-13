

from django.contrib import admin
from django.urls import path, include
from profile.views import (
    RegisterView,
    LoginView,
    LogoutView,

    #demo
    RegisterDemoView,
    LoginDemoView,
    LogoutDemoView,
    )

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shop/", include('shop.urls')),
    path("profile/", include('profile.urls')),  
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),  

    #demo
        path('register/', RegisterDemoView.as_view(), name='register-demo'),
    path('login/', LoginDemoView.as_view(), name='login-demo'),
    path('logout/', LogoutDemoView.as_view(), name='logout-demo'),
]
