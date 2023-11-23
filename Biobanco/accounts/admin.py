from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username',  'date_joined',
                    'last_login', 'is_admin', 'is_tecnico', 'is_supervisor')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    filter_hotizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
