from django.contrib import admin
from django.urls import path, include
from frontend.views import HomeView, ProfileView, ShopView
from profile.views import RegisterView, LoginView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API Endpoints
    path("api/shop/", include('shop.urls')),
    path("api/profile/", include('profile.urls')),
    path('api/register/', RegisterView.as_view(), name='register_api'),
    path('api/login/', LoginView.as_view(), name='login_api'),
    path('api/logout/', LogoutView.as_view(), name='logout_api'),
    
    # HTML Views
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('shop/', ShopView.as_view(), name='shop'),
]
