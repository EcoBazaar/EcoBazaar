

from django.contrib import admin
from django.urls import path, include
from profile.views import RegisterView, LoginView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shop/", include('shop.urls')),
    path("api/profile/", include('profile.urls')),  
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),  

    #demo
    path('login/', LoginView.as_view(), name='login'),
]
