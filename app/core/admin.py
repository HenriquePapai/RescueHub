from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Animal, AdoptionRequest, AuditLog

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

#Gerenciamento de Pedidos e logs no painel Admin
@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ['animal', 'adotante', 'status', 'created_at']
    list_filter = ['status']

#Os logs não são alteráveis
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['adoption_request', 'user', 'action', 'timestamp']
    list_filter = ['user', 'timestamp']
    readonly_fields = ['adoption_request', 'user', 'action', 'timestamp']