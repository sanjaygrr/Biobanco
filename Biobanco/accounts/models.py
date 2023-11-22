from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver

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
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

    def get_by_natural_key(self, email):
        return self.get(email=self.normalize_email(email)) 
    
    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

#is_admin: Administrador
#is_staff: personal Técnico
#is_superuser: Supervisor 

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(
        verbose_name="username", max_length=30)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    user_state = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    #groups(roles) for users
    class Role(models.TextChoices):
        ADMIN = "Administrador", "Administrador"
        SUPERVISOR = "Supervisor", "Supervisor"
        TECNICO = "Tecnico", "Técnico"
        

    base_role = Role.OTHER 

    role = models.CharField(max_length=50, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **args)
    
#group supervisor
class SupervisorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Account.Role.SUPERVISOR)

class Supervisor(Account):

    base_role = Account.Role.SUPERVISOR

    supervisor = SupervisorManager() 

    class Meta:
        proxy = True
    
    def tipo_role(self):
        return "Sólo para rol de Supervisor" 
    
#@receiver(post_save, sender=Supervisor)
#def create_account_profile(sender, instance, created, **kwargs):
#    if created and instance.role == "SUPERVISOR":
#        SupervisorProfile.objects.create(user=instance)

#class SupervisorProfile(models.Model): 
#   user = models.OneToOneField(Account, on_delete=models.CASCADE)
#   supervisor_id = models.IntegerField(null=True, blank=True)



#group técnico
class TecnicoManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=Account.Role.TECNICO)

class Tecnico(Account):

    base_role = Account.Role.TECNICO

    tecnico = TecnicoManager() 

    class Meta:
        proxy = True
    
    def tipo_role(self):
        return "Sólo para rol de Técnico" 
    
#@receiver(post_save, sender=Tecnico)
#def create_account_profile(sender, instance, created, **kwargs):
#   if created and instance.role == "TECNICO":
#        TecnicoProfile.objects.create(user=instance)

#class TecnicoProfile(models.Model): 
#   user = models.OneToOneField(Account, on_delete=models.CASCADE)
#   tecnico_id = models.IntegerField(null=True, blank=True)


