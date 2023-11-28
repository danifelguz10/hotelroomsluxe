from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Room, Reservation, UserProfile, UserProfileGroup

# Define una clase de administración personalizada para UserProfile
class UserProfileAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'get_roles')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')

    # Corrige el ordenamiento para usar 'email' en lugar de 'username'
    ordering = ('email',)

    def get_roles(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])

    get_roles.short_description = 'Roles'

# Registra UserProfile con su clase de administración personalizada
admin.site.register(UserProfile, UserProfileAdmin)

class UserProfileGroupAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')
    search_fields = ('user__email', 'group__name')

admin.site.register(UserProfileGroup, UserProfileGroupAdmin)

# Define una clase de administración personalizada para Room
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'description', 'price', 'ammount', 'state')
    search_fields = ('number', 'description', 'state')
    list_filter = ('state',)

# Registra Room con su clase de administración personalizada
admin.site.register(Room, RoomAdmin)

# Define una clase de administración personalizada para Reservation
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in_date', 'check_out_date', 'status')
    search_fields = ('user__email', 'room__number', 'status')
    list_filter = ('status',)

# Registra Reservation con su clase de administración personalizada
admin.site.register(Reservation, ReservationAdmin)
