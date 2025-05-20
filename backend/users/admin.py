from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff')
    search_fields = ('username', 'email')

    fieldsets = (
        (
            '', {'fields': ('username', 'email', 'password')}
        ),
        (
            'Personal info', {'fields': ('first_name', 'last_name')}
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            },
        ),
        (
            'Important dates', {'fields': ('last_login', 'date_joined')}
        ),
    )

    add_fieldsets = (
        (
            'Создание пользователя',
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2'),
            },
        ),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
