from django.db import models
from IQbackend.mixins import base  
from django.dispatch import receiver
from django.db.models.signals import post_save


from architectural_plans.models import ArchitecturalPlan
from authentication.models import User


class ProfileSettings(base.UUIDCreatedUpdatedMixin, models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="profile_settings"
    )
    profile_picture = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="Path of s3 uploaded profile picture"
    )
    preferred_property_type = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    preferred_home_style = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    preferred_construction_material = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    industry = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    company = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    job_title = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    years_of_experience = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )
    home_built_per_year = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    license_number = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    bio = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=""
    )
    primary_service_area = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    state = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    province = models.CharField(
        max_length=255, 
        null=True,
        blank=True,
        help_text=""
    )
    zip_postal_code = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    website_url = models.URLField(
        null=True,
        blank=True,
        help_text="",
    )
    linkedin_profile = models.URLField(
        null=True,
        blank=True,
        help_text=""
    )
    instagram_profile = models.URLField(
        null=True,
        blank=True,
        help_text=""
    )
    twitter_profile = models.URLField(
        null=True,
        blank=True,
        help_text=""
    )
    facebook_page = models.URLField(
        null=True,
        blank=True,
        help_text=""
    )
    
    def __str__(self):
        return f"ProfileSettings - {self.user.username}"
    

@receiver(post_save, sender=User)
def create_profile_settings(sender, instance=None, created=False, **kwargs):
    if created:
        ProfileSettings.objects.create(user=instance)


class Report(base.UUIDCreatedUpdatedMixin, models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="reports"
    )
    address = models.CharField(
        max_length=255, 
        help_text=""
    )
    property = models.JSONField(
        blank=True, 
        null=True
    )
    kpis = models.JSONField(
        blank=True, 
        null=True
    ) 
    comparable_sales = models.JSONField(
        blank=True, 
        null=True
    )
    zoning = models.JSONField(
        blank=True, 
        null=True
    ) 
    architectural_plans = models.ManyToManyField(
        ArchitecturalPlan
    ) 
    selected_plan = models.ForeignKey(
        ArchitecturalPlan, 
        on_delete=models.CASCADE,
        related_name="selected_in_reports",
        blank=True, 
        null=True
    )
    acquisition_cost = models.FloatField(
        default=0.0,
        help_text="Other acquisition cost listed in dashboard kpis"
    )
    other_cost = models.FloatField(
        default=0.0,
        help_text="Other development cost listed in dashboard kpis"
    )

    class Meta:
        unique_together = ('user', 'address')

    def __str__(self):
        return f"Report - {self.address} - {self.user.username}"