from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from helpers.models import BaseModel


class CustomAccountManager(BaseUserManager):

    def create_superuser(
            self,
            address,
            referral_username,
            **other_fields
    ):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        return self.create_user(
            address,
            referral_username,
            **other_fields
        )

    def create_user(
            self,
            address,
            referral_username,
            **other_fields
    ):
        user = self.model(
            address=address,
            referral_username=referral_username,
            **other_fields
        )
        user.save()
        return user


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    address = models.CharField(max_length=150, unique=True, db_index=True)
    referral_username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    referrer_username = models.CharField(max_length=100, blank=True, null=True)
    referral_count = models.IntegerField(default=0)
    last_rewarded_referral_count = models.IntegerField(default=0)
    twitter_task = models.IntegerField(default=0)
    telegram_task = models.IntegerField(default=0)
    whitelist_task = models.IntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'address'
    
    def __str__(self):
        return self.address