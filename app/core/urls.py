from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('catalogo/', views.catalog, name='catalog'),
    path('animais/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animais/novo/', views.animal_create, name='animal_create'),
    path('animais/<int:pk>/editar/', views.animal_edit, name='animal_edit'),
]