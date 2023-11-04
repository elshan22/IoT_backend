from argparse import Action
#from msilib.schema import Control
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import os

def upload_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"users/{instance.pk}/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, user_name, first_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, first_name, password, **other_fields)
        # user = self.model(
        #     email=self.normalize_email(email),
        #     username=username,
        # )
        # user.set_password(password)
        # user.save(using=self._db)
        # return user

    def create_user(self, email, user_name, first_name, password, **otherfields):

        if not email:
            raise ValueError("Users must have an email address")
        if not user_name:
            raise ValueError("Users must have an Username")

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                          first_name=first_name, **otherfields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_MANAGER = 'M'
    ROLE_SYSTEM = 'S'
    ROLE_Customer = 'C'

    ROLE_CHOICES = [
        (ROLE_MANAGER, 'Manager'),
        (ROLE_SYSTEM, 'System'),
        (ROLE_Customer, 'Customer'),
    ]
    # start_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    user_name = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=30)
    start_date = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=ROLE_Customer)
    # is_admin = models.BooleanField()
    # is_superuser = models.BooleanField()
    about = models.TextField(_(
        'about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'first_name']

    def __str__(self):
        return self.user_name

    # def has_perm(self, perm, obj=None):
    #     return self.is_admin
    #
    # def has_module_perms(self, app_label):
    #     return True
# class CustomUser(AbstractBaseUser):
#     ROLE_MANAGER = 'M'
#     ROLE_SYSTEM = 'S'
#     ROLE_Customer = 'C'
#
#     ROLE_CHOICES = [
#         (ROLE_MANAGER, 'Manager'),
#         (ROLE_SYSTEM, 'System'),
#         (ROLE_Customer, 'Customer'),
#     ]
#     email = models.EmailField(verbose_name="email", max_length=60, unique=True)
#     username = models.CharField(max_length=30, unique=True)
#     password = models.CharField(max_length=30)
#     data_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
#     last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
#     role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=ROLE_Customer)
#     is_admin = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', ]
#
#     objects = CustomUserManager()
#
#     def __str__(self):
#         return self.email + " ," + self.username
#
#     def has_perm(self, perm, obj=None):
#         return self.is_admin
#
#     def has_module_perms(self, app_label):
#         return True

class Node(models.Model):
    ErrorId=models.IntegerField(null=True, blank=True)
    MacAddress=models.CharField(max_length=100,null=True,blank=True)
    SetPointTemperature=models.FloatField(null=True,blank=True)
    permissions=models.BooleanField(null=True, blank=True)
    status=models.BooleanField(null=True, blank=True)
    mode=models.CharField(max_length=500,null=True, blank=True)
    name=models.CharField(max_length=500,null=True, blank=True)
    LastTime=models.DateTimeField(null=True, blank=True)
class NodeStation(models.Model):
    DateTime=models.DateTimeField(null=True, blank=True)
    Node=models.ForeignKey(Node,on_delete=models.CASCADE)
    Presence=models.IntegerField(null=True, blank=True)
    ErrorId=models.IntegerField(null=True, blank=True)
    FanCoilTemperature=models.FloatField(null=True,blank=True)
    HomeTemperature=models.FloatField(null=True, blank=True)
    status=models.BooleanField(null=True, blank=True)
    faucetState=models.CharField(max_length=100,null=True, blank=True)
    SetPointTemperature=models.FloatField(null=True,blank=True)
    name=models.CharField(max_length=500,null=True, blank=True)
    humidity=models.FloatField(null=True,blank=True)
    valveState1=models.BooleanField(null=True,blank=True)
    valveState2=models.BooleanField(null=True,blank=True)
    FanCoil1=models.FloatField(null=True,blank=True) 
    FanCoil2=models.FloatField(null=True,blank=True) 
    light=models.FloatField(null=True,blank=True)
    analog1=models.FloatField(null=True,blank=True)
    analog2=models.FloatField(null=True,blank=True)
    fanState1=models.BooleanField(null=True,blank=True)
    fanState2=models.BooleanField(null=True,blank=True)
    LastTime=models.DateTimeField(null=True, blank=True)
    #HvacMode=models.CharField(max_length=500,null=True, blank=True)
    #HvacTemp1=models.FloatField(null=True, blank=True)
    #HvacTemp2=models.FloatField(null=True, blank=True)
    #HvacType=models.CharField(max_length=500,null=True, blank=True)
    #numFans=models.IntegerField(null=True, blank=True)
class Neighbor(models.Model):
    Node1=models.ForeignKey(Node,on_delete=models.CASCADE,related_name='Neighbor1')
    Node2=models.ForeignKey(Node,on_delete=models.CASCADE)
    RSSI=models.FloatField(null=True,blank=True)


class Allocation(models.Model):
    userId=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    NodeId=models.ForeignKey(Node,on_delete=models.CASCADE)
    StartDate=models.DateField(null=True, blank=True)
    EndDate=models.DateTimeField(null=True, blank=True)
    
class UserNode(models.Model):
    DateTime=models.DateTimeField(auto_now_add=True)
    Action=models.CharField(max_length=100,null=True, blank=True)
    
class Security(models.Model):
    Name=models.CharField(max_length=100)
    Value=models.CharField(max_length=100,null=True,blank=True)
    
class SecurityStation(models.Model):
    Name=models.CharField(max_length=100)
    Value=models.BooleanField()
    DateTime=models.DateTimeField(auto_now_add=True)
    
class FanCoil(models.Model):
    Node=models.ForeignKey(Node,on_delete=models.CASCADE)
    valv=models.BooleanField(null=True, blank=True)
    valvstate=models.BooleanField(null=True, blank=True)
    Temperature=models.FloatField(null=True, blank=True)
    LastTime=models.FloatField(null=True,blank=True)

class FanCoilStation(models.Model):
    FanCoilId=models.ForeignKey(FanCoil,on_delete=models.CASCADE)
    valv=models.BooleanField(null=True, blank=True)
    valvstate=models.BooleanField(null=True, blank=True)
    Temperature=models.FloatField(null=True, blank=True)
   
class Floor(models.Model):
    image=models.ImageField(_("Image"),upload_to=upload_to, null=True, blank=True)
    
class MatFile(models.Model):
    File=models.FileField(_("File"),upload_to=upload_to, null=True, blank=True)
class switch(models.Model):
    index=models.CharField(max_length=100,null=True,blank=True)