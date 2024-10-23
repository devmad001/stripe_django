from IQbackend.mixins import base
from django.contrib.gis.db import models

class GISZoningCode(base.UUIDCreatedUpdatedMixin, models.Model):
    city = models.CharField(max_length=50,
                            null=True,
                            blank=True,
                            help_text="Name of the city where the zoning area is located.")
    state = models.CharField(max_length=50,
                            null=True,
                            blank=True,
                            help_text="Name of the state where the zoning area is located.")
    municode_zoning_code = models.CharField(max_length=50,
                            null=True,
                            blank=True,
                            help_text="Zoning code mentioned in municode zoning rules.")
    gis_zoning_code = models.CharField(max_length=50,
                            null=True,
                            blank=True,
                            help_text="Zoning code mentioned in gis zoning rules.")

    def __str__(self):
        return f"GISZoningCode - {self.city} - {self.gis_zoning_code}"
    
class GISZoning(base.UUIDCreatedUpdatedMixin, models.Model):
    object_id = models.FloatField(null=True, 
                                  blank=True, 
                                  help_text="Unique identifier for the zoning object, typically used for internal reference.")
    zone_type = models.CharField(max_length=254, 
                                 null=True, 
                                 blank=True, 
                                 help_text="Type of zoning (e.g., residential, commercial, industrial).")
    zoning_desc = models.CharField(max_length=254, 
                                   null=True, 
                                   blank=True, 
                                   help_text="Detailed description of the zoning designation.")
    ordinance = models.CharField(max_length=254, 
                                 null=True, 
                                 blank=True, 
                                 help_text="Reference to the ordinance or legal document defining the zoning regulations.")
    city = models.CharField(max_length=50, 
                            null=True, 
                            blank=True, 
                            help_text="Name of the city where the zoning area is located.")
    geom = models.GeometryField(null=True, 
                                blank=True, 
                                help_text="Geometric representation of the zoning area, typically stored as polygons or multipolygons.")

    def __str__(self):
        return f"GISZoning - {self.id}"
