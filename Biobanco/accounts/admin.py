from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account, Role


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined',
                    'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    # Aquí agregamos ROLE_id_role a fieldsets y add_fieldsets
    fieldsets = (
        (None, {'fields': ('email', 'username',
         'password', 'name', 'lastname', 'ROLE_id_role')}),
        ('Permissions', {'fields': ('is_admin',
         'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Este es el fieldset para la creación de un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'lastname', 'ROLE_id_role', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ()
    list_filter = ()

    def save_model(self, request, obj, form, change):
        """
        Aquí puedes añadir lógica adicional al guardar el modelo,
        como asignar un rol por defecto si no se ha seleccionado ninguno.
        """
        super().save_model(request, obj, form, change)


admin.site.register(Account, AccountAdmin)
admin.site.register(Role)  # Asegúrate de registrar también el modelo Role
