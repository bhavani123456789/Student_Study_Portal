from django.contrib import admin
from django.urls import include, path
from dashboard import views as dash_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),  # Assuming 'dashboard.urls' contains your app URLs
    path('register/', dash_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name="dashboard/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Changed to LogoutView
    path('profile/', dash_views.profile, name='profile'),
]
