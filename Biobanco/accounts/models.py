from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _



#class Role(models.Model):
#    id_role = models.AutoField(primary_key=True)
#    role_name = models.CharField(max_length=15, null=False, blank=False)

#    def __str__(self):
#        return self.role_name

#    class Meta:
#        db_table = 'ROLE'


# class User(models.Model):
#    id_user = models.CharField(max_length=20, primary_key=True)
#    name = models.CharField(max_length=20)
#    lastname = models.CharField(max_length=20)
#    email = models.CharField(max_length=20)
#    user_state = models.CharField(max_length=20)
#    password_hash = models.CharField(max_length=20)
#    ROLE_id_role = models.ForeignKey(Role, on_delete=models.CASCADE)

#    def __str__(self):
#        return f"{self.name} {self.lastname}"

#    class Meta:
#        db_table = 'USER'



class MyAccountManager(BaseUserManager):

    def create_user(self, email, username,  password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password,):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_tecnico = True
        user.is_supervisor = True
        user.save(using=self._db)

    def get_by_natural_key(self, email):
        return self.get(email=self.normalize_email(email))


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(
        verbose_name="username", max_length=30)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    user_state = models.BooleanField(default=True)
    is_tecnico = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
#is_admin: Administrador
#is_tecnico: personal Técnico
#is_supervisor: Supervisor 

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(
        verbose_name="username", max_length=30)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    user_state = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_tecnico = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    
    
    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    


class Role(Group):
    class Meta:
        proxy = True
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    #Creación de grupos
    @classmethod
    def create_roles_with_permissions(cls):
    
        admin_role, _ = Group.objects.get_or_create(name='administrador')
        tecnico_role, _ = Group.objects.get_or_create(name='tecnico')
        supervisor_role, _ = Group.objects.get_or_create(name='supervisor')

    #Creación de permisos asociados a los grupos
    #COMPLETAR codename___in con los nombrados en @permission_required en muestras.views
        admin_permissions = Permission.objects.filter(codename__in=[

        ])
        admin_role.permissions.add(*admin_permissions)
        

        tecnico_permissions = Permission.objects.filter(codename__in=[

        ])
        tecnico_role.permissions.add(*tecnico_permissions) 
        

        supervisor_permissions = Permission.objects.filter(codename__in=[
            
        ])
        supervisor_role.permissions.add(*supervisor_permissions) 
