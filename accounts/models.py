from django.db import models
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _



class UserManager(BaseUserManager):
    '''
    created normal and superuser for app!
    '''
    def create_user(self,email,password,**extra_fields):
        # Normalize email, set defaults, and persist a new user.
        if not email:
            raise ValueError(_('Email must be set!'))
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password,**extra_fields):
        # Enforce superuser flags before delegating to create_user.
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_verified',True)
        
        '''
        this part is to make sure that is_staff and is_superuser 
        are set to true for newly created superuser!
        '''
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True!'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True!'))
        return self.create_user(email,password,**extra_fields)


class User(AbstractBaseUser,PermissionsMixin):
    '''
    custom user model for app!
    '''
    email = models.EmailField(max_length=255,unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()
    def __str__(self):
        # Return the email for admin and display usage.
        return self.email
