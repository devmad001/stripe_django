from django.db import models
from IQbackend.mixins import base  
from authentication.models import User
from architectural_plans.data_types import * 

class ExteriorWallType(models.Model):
    WALL_TYPES = [
        (ExteriorWall24.TYPE, ExteriorWall24.DESC),
        (ExteriorWall26.TYPE, ExteriorWall26.DESC),
        (ExteriorWall28.TYPE, ExteriorWall28.DESC),
        (ExteriorWallICF.TYPE, ExteriorWallICF.DESC),
        (ExteriorContainer.TYPE, ExteriorContainer.DESC),
        (Exterior66Post.TYPE, Exterior66Post.DESC),
        (ExteriorBlockCMU.TYPE, ExteriorBlockCMU.DESC),
        (ExteriorMetal.TYPE, ExteriorMetal.DESC),
        (ExteriorPostFrame.TYPE, ExteriorPostFrame.DESC),
        (ExteriorLog.TYPE, ExteriorLog.DESC),
        (ExteriorBlockBothLevel.TYPE, ExteriorBlockBothLevel.DESC)
    ]
    name = models.CharField(max_length=255, choices=WALL_TYPES, help_text="Types of exterior walls like 2x4, 2x6 etc", default=None)
    
    def __str__(self):
        return self.name
class Foundation(models.Model):
    FOUNDATION_TYPES = [
        (FoundationBasement.TYPE, FoundationBasement.DESC),
        (FoundationCrawl.TYPE, FoundationCrawl.DESC),
        (FoundationRaiseIsland.TYPE, FoundationRaiseIsland.DESC),
        (FoundationPostFrame.TYPE, FoundationPostFrame.DESC),
        (FoundationDaylight.TYPE, FoundationDaylight.DESC),
        (FoundationWalkout.TYPE, FoundationWalkout.DESC),
        (FoundationMonolithicSlab.TYPE, FoundationMonolithicSlab.DESC),
        (FoundationComboBasementCrawl.TYPE, FoundationComboBasementCrawl.DESC),
        (FoundationPostBeam.TYPE, FoundationPostBeam.DESC),
        (FoundationStemWall.TYPE, FoundationStemWall.DESC),
        (FoundationPostPier.TYPE, FoundationPostPier.DESC),
        (FoundationPier.TYPE, FoundationPier.DESC),
        (FoundationSlab.TYPE, FoundationSlab.DESC),
        (FoundationPiling.TYPE, FoundationPiling.DESC),
        (FoundationJoist.TYPE, FoundationJoist.DESC),
        (FoundationComboSlabCrawl.TYPE, FoundationComboSlabCrawl.DESC)
    ]
    name = models.CharField(max_length=255, help_text="Type of foundation like slab, basement, wall etc", default=None)

    def __str__(self):
        return self.name

class GarageLocation(models.Model):
    GARAGE_LOCATIONS = [
        (GarageLocationFront.TYPE, GarageLocationFront.DESC),
        (GarageLocationSide.TYPE, GarageLocationSide.DESC),
        (GarageLocationRear.TYPE, GarageLocationRear.DESC),
        (GarageLocationCourtyard.TYPE, GarageLocationCourtyard.DESC)
    ]
    name = models.CharField(max_length=255, choices=GARAGE_LOCATIONS, help_text="Location of garage i.e. side, front or courtyard etc", default=None)

    def __str__(self):
        return self.name

class GarageType(models.Model):
    GARAGE_TYPES = [
        (GarageTypeDriveUnder.TYPE, GarageTypeDriveUnder.DESC),
        (GarageTypeAttached.TYPE, GarageTypeAttached.DESC),
        (GarageTypeDetached.TYPE, GarageTypeDetached.DESC),
        (GarageTypeRVGarage.TYPE, GarageTypeRVGarage.DESC),
        (GarageTypeCarport.TYPE, GarageTypeCarport.DESC)
    ]
    name = models.CharField(max_length=255, choices=GARAGE_TYPES, help_text="Type of garage like attached, detached or none etc", default=None)

    def __str__(self):
        return self.name
    
class ArchitecturalPlan(base.UUIDCreatedUpdatedMixin, models.Model):
    ARCHITECTURAL_STYLES = [
        (StyleCoastalContemporary.TYPE, StyleCoastalContemporary.DESC),
        (StyleNorthwest.TYPE, StyleNorthwest.DESC),
        (StyleCountry.TYPE, StyleCountry.DESC),
        (StyleVictorian.TYPE, StyleVictorian.DESC),
        (StyleNewOrleans.TYPE, StyleNewOrleans.DESC),
        (StyleNewAmerican.TYPE, StyleNewAmerican.DESC),
        (StyleAFrame.TYPE, StyleAFrame.DESC),
        (StyleShingle.TYPE, StyleShingle.DESC),
        (StyleSouthern.TYPE, StyleSouthern.DESC),
        (StyleBeach.TYPE, StyleBeach.DESC),
        (StyleTraditional.TYPE, StyleTraditional.DESC),
        (StyleFlorida.TYPE, StyleFlorida.DESC),
        (StyleSouthwest.TYPE, StyleSouthwest.DESC),
        (StyleLouisiana.TYPE, StyleLouisiana.DESC),
        (StyleLog.TYPE, StyleLog.DESC),
        (StyleTudor.TYPE, StyleTudor.DESC),
        (StyleFarmhouse.TYPE, StyleFarmhouse.DESC),
        (StyleModern.TYPE, StyleModern.DESC),
        (StyleFrenchCountry.TYPE, StyleFrenchCountry.DESC),
        (StyleHillCountry.TYPE, StyleHillCountry.DESC),
        (StyleLakeHouse.TYPE, StyleLakeHouse.DESC),
        (StyleCottage.TYPE, StyleCottage.DESC),
        (StyleAcadian.TYPE, StyleAcadian.DESC),
        (StyleRanch.TYPE, StyleRanch.DESC),
        (StyleMidCenturyModern.TYPE, StyleMidCenturyModern.DESC),
        (StyleSouthernTraditional.TYPE, StyleSouthernTraditional.DESC),
        (StyleRustic.TYPE, StyleRustic.DESC),
        (StyleScandinavian.TYPE, StyleScandinavian.DESC),
        (StyleBarndominium.TYPE, StyleBarndominium.DESC),
        (StyleCapeCod.TYPE, StyleCapeCod.DESC),
        (StyleCoastal.TYPE, StyleCoastal.DESC),
        (StyleGeorgian.TYPE, StyleGeorgian.DESC),
        (StyleCraftsman.TYPE, StyleCraftsman.DESC),
        (StyleCarriage.TYPE, StyleCarriage.DESC),
        (StyleColonial.TYPE, StyleColonial.DESC),
        (StyleModernFarmhouse.TYPE, StyleModernFarmhouse.DESC),
        (StyleBungalow.TYPE, StyleBungalow.DESC),
        (StyleContemporary.TYPE, StyleContemporary.DESC),
        (StyleAdobe.TYPE, StyleAdobe.DESC),
        (StylePrairie.TYPE, StylePrairie.DESC),
        (StyleCabin.TYPE, StyleCabin.DESC),
        (StyleLowCountry.TYPE, StyleLowCountry.DESC),
        (StyleVacation.TYPE, StyleVacation.DESC),
        (StyleEuropean.TYPE, StyleEuropean.DESC),
        (StyleMediterranean.TYPE, StyleMediterranean.DESC),
        (StyleMountain.TYPE, StyleMountain.DESC)
    ]
    plan_number = models.CharField(
        max_length=20,
        help_text="Plan number to uniquely identify architectural plan on source website"
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the plan"
    )
    image_link = models.URLField(
        help_text="Image of the plan"
    )
    architectural_style = models.CharField(
        max_length=100,
        choices=ARCHITECTURAL_STYLES,
        help_text="Architectural style for the building",
        default=None
    )
    area_total = models.FloatField(
        default=0.0,
        help_text="Total area required to build on the plan"
    )
    bedrooms_count = models.FloatField(
        default=0.0,
        help_text="Total bedrooms included in plan"
    )
    bathrooms_count = models.FloatField(
        default=0.0,
        help_text="Total bathrooms included in plan. This is calculated based on bathrooms_full_count and bathrooms_half_count."
    )
    bathrooms_full_count = models.FloatField(
        default=0.0,
        help_text="Each of the value is counted as 1 unit in bathrooms_count"
    )
    bathrooms_half_count = models.FloatField(
        default=0.0,
        help_text="Each of the value is counted as 0.5 in bathrooms_count"
    )
    stories = models.FloatField(
        default=0.0,
        help_text="Number of floors in the architectural plan"
    )
    area_first_floor = models.FloatField(
        default=0.0,
        help_text="Area of first floor"
    )
    area_second_floor = models.FloatField(
        default=0.0,
        help_text="Area of second floor"
    )
    area_third_floor = models.FloatField(
        default=0.0,
        help_text="Area of third floor"
    )
    area_basement = models.FloatField(
        default=0.0,
        help_text="Area of basement"
    )
    area_garage = models.FloatField(
        default=0.0,
        help_text="Area of garage"
    )
    cars_capacity = models.FloatField(
        default=0.0,
        help_text="Number of cars that can be parked in garage"
    )
    width = models.FloatField(
        default=0.0,
        help_text="Width required to build based on the plan"
    )
    depth = models.FloatField(
        default=0.0,
        help_text="Depth required to build based on the plan"
    )
    height = models.FloatField(
        default=0.0,
        help_text="Height required to build based on the plan"
    )
    buy_url = models.URLField(
        help_text="Url to buy plan from the source website"
    )
    units = models.FloatField(
        default=0.0,
        help_text="Units correspond to plan types like single family, stand alone etc"
    )
    garage_location = models.ManyToManyField(
        GarageLocation
    )
    garage_type = models.ManyToManyField(
        GarageType
    )
    foundation = models.ManyToManyField(
        Foundation
    )
    exterior_wall_type = models.ManyToManyField(
        ExteriorWallType
    )

    def __str__(self):
        return f"ArchitecturalPlan - {self.title} - {self.plan_number}"


class FavoritePlan(base.UUIDCreatedUpdatedMixin, models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="favorite_plans"
    )
    architectural_plan = models.ForeignKey(
        ArchitecturalPlan, 
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )

    def __str__(self):
        return f"FavoritePlan - {self.user.username} {self.architectural_plan.title}"
