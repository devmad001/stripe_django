from django.db import models
from IQbackend.mixins import base

class AttomData(base.UUIDCreatedUpdatedMixin, models.Model):
    address = models.CharField(max_length=500, 
                               unique=True, 
                               help_text="Address including street, city, state, country")
    comparable_sales = models.JSONField(null=True, 
                                        blank=True, 
                                        help_text="Comparable sales data received from attom")
    property = models.JSONField(null=True, 
                                blank=True, 
                                help_text="Property data received from attom")
    
    def __str__(self):
        return f"AttomData - {self.id} - {self.address}"