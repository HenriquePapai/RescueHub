from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Animal


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (('Perfil', {'fields': ('role', 'phone')}),)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'sex', 'age', 'size', 'status']
    list_filter = ['species', 'status']
    search_fields = ['name']