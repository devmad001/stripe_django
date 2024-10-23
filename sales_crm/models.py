from django.db import models
from IQbackend.mixins import base

class WaitlistUser(base.UUIDCreatedUpdatedMixin, models.Model):
    first_name = models.CharField(
        max_length=255,
        help_text="Enter the first name of the individual joining the waitlist."
    )
    last_name = models.CharField(
        max_length=255,
        help_text="Enter the last name of the individual joining the waitlist."
    )
    email = models.EmailField(
        unique=False,
        help_text="Enter the email address of the individual joining the waitlist."
    )
    occupation = models.CharField(
        max_length=255,
        help_text="Enter the occupation of the individual joining the waitlist."
    )
    comments = models.TextField(
        max_length=2000, 
        help_text="Field to store user comments", 
        null=True, 
        blank=True)

    def __str__(self):
        return f"WaitlistCommercial - {self.first_name} {self.last_name}"

class MContactInfo(base.UUIDCreatedUpdatedMixin, models.Model):
    first_name = models.CharField(
        max_length=255,
        help_text="Enter the first name of the municipal contact."
    )
    last_name = models.CharField(
        max_length=255,
        help_text="Enter the last name of the municipal contact."
    )
    email = models.EmailField(
        unique=True,
        help_text="Enter the email address of the municipal contact."
    )
    phone = models.CharField(
        unique=True,
        max_length=20,
        help_text="Enter the phone number of the municipal contact, including area code."
    )
    municipality = models.CharField(
        max_length=255,
        help_text="Enter the name of the municipality."
    )
    residential_permits_qty = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Enter the number of residential permits requests received in 2023 (optional)."
    )
    commercial_permits_qty = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Enter the number of commercial permits requests received in 2023 (optional)."
    )
    approving_requests = models.BooleanField(
        default=True,
        help_text="Indicate whether the contact is currently approving requests."
    )

    def __str__(self):
        return f"MunicipalityUser - {self.first_name} {self.last_name}"
