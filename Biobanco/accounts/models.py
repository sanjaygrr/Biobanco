from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission


class MyAccountManager(BaseUserManager):

    def create_user(self, email, username, password=None, name=None, lastname=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
            lastname=lastname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )

        # Assign the role after creating the user
        role_admin = Role.objects.get(id_role=Role.ADMIN)
        user.ROLE_id_role = role_admin

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)


class Role(models.Model):
    ADMIN = 1
    SUPERVISOR = 2
    TECNICO = 3

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (SUPERVISOR, 'Supervisor'),
        (TECNICO, 'Technician'),
    )

    id_role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, primary_key=True)

    
    #def role_with_permissions(cls):

    #   admin_role = Group.objects.get_or_create(ADMIN) 

    
    
    def __str__(self):
        return self.get_id_role_display()


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(
        verbose_name="username", max_length=30, unique=True)
    name = models.CharField(max_length=20, null=True)
    lastname = models.CharField(max_length=20, null=True)
    ROLE_id_role = models.ForeignKey(
        Role, on_delete=models.CASCADE, default=Role.ADMIN)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    user_state = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    #def has_perm(self, perm, obj=None):
    #   return self.is_admin

    def has_module_perms(self, app_label):
        return True

