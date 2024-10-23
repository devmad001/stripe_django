from django.db import models
from django.contrib.auth.models import AbstractUser   
from IQbackend.mixins import base  
from authentication.users import (
    UserRoleMunicipality,
    UserRoleCommercial,
    UserRoleAdmin
)


class User(base.UUIDCreatedUpdatedMixin, AbstractUser):
    phone = models.CharField(
        max_length=15, 
        help_text=""
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=""
    )

    def __str__(self):
        return f"User - {self.username}"


class UserRole(base.UUIDCreatedUpdatedMixin, models.Model):
    USER_ROLES = [
        (UserRoleMunicipality.TYPE, UserRoleMunicipality.DESC),
        (UserRoleCommercial.TYPE, UserRoleCommercial.DESC),
        (UserRoleAdmin.TYPE, UserRoleAdmin.DESC),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="roles"
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        help_text=""
    ) 


class MunicipalityUser(models.Model):
    municipality = models.CharField(
        max_length=255, 
        help_text=""
    )
    residential_permits_qty = models.PositiveIntegerField(
       null=True,
       blank=True
    )
    commercial_permits_qty = models.PositiveIntegerField(
       null=True,
       blank=True
    )
    approving_requests = models.BooleanField(
        default=True,
        help_text=""
    )
    status = models.BooleanField(
        default=True,
        help_text=""
    )

    def __str__(self):
        return f"MunicipalityUser - {self.user.username}"


class CommercialUser(models.Model):
    municipality = models.CharField(
        max_length=255,
        help_text=""
    )
    rpr = models.CharField(
        max_length=100,
        help_text=""
    )
    cpr = models.CharField(
        max_length=100,
        help_text=""
    )
    interested = models.BooleanField(
        default=True,
        help_text=""
    )
    status = models.BooleanField(
        default=True,
        help_text=""
    )

    def __str__(self):
        return f"CommercialUser - {self.user.username}"


class SessionData(base.UUIDCreatedUpdatedMixin, models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="session_data"
    )
    session_id = models.CharField(
        max_length=255,
        help_text="Django session ID"
    )
    property = models.JSONField(null=True, blank=True)
    zoning = models.JSONField(null=True, blank=True)
    user_choices = models.JSONField(null=True, blank=True)
    query_property = models.JSONField(null=True, blank=True)
    kpi = models.JSONField(null=True, blank=True)
    architectural_plans = models.JSONField(null=True, blank=True)
    selected_architectural_plan = models.JSONField(null=True, blank=True)
    comparables = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"SessionData - {self.user.username} - {self.session_id}"