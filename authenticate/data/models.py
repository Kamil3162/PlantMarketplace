from datetime import timedelta

from django.utils import timezone

from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AccessToken(models.Model):
    user = models.UUIDField(
        null=False
    )
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_blacklisted = models.BooleanField(default=False)


class RefreshToken(models.Model):
    user_id = models.UUIDField()
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        lifetime_days = getattr(settings, "TOKEN_LIFETIME_DAYS", 7)
        self.expires_at = timezone.now() + timedelta(days=lifetime_days)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('created_at', )

class BlackListedTokens(models.Model):
    user = models.UUIDField(
        null=False
    )
    banned_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ResetPasswordToken(models.Model):
    user = models.UUIDField()
    reset_token = models.CharField()
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    def check_expiration(self):
        if current_time:=timezone.now() > self.expires_at:
            return False
        return True

    def save(self, *args, **kwargs):
        lifetime_days = getattr(settings, "TOKEN_LIFETIME_DAYS", 7)
        actual_time = timezone.now()
        self.expires_at = actual_time + timedelta(days=lifetime_days)
        self.created_at = actual_time
        super().save(*args, **kwargs)