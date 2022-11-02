# Register your models here.

from django.contrib import admin
from .models import Crmuser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username','contact')
    list_filter = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username','contact')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username','contact', 'password', 'password_conformation'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
# Now register the new UserAdmin...
admin.site.register(Crmuser, UserAdmin)
