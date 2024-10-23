from django.db.models import Q
from users.models import Report
from django.core.paginator import Paginator
from architectural_plans.models import ArchitecturalPlan
from zoning.helpers import applyZoningRules

def applyBedBathFilters(field_name, values):
    q_objects = Q()
    for value in values:
        if value.endswith('+'):
            value = float(value.rstrip('+'))
            q_objects |= Q(**{f"{field_name}__gte": value})
        else:
            q_objects |= Q(**{field_name: float(value)})
    return q_objects

def getArchitecturalPlans(request, address, architectural_style = None, area_total_min = None, area_total_max = None, width_min = None, width_max = None, height_min = None, height_max = None, depth_min = None, depth_max = None, stories = None, cars_capacity = None, foundation = None, exterior_wall_type = None, garage_type = None, units = None, bedrooms = None, bathrooms = None, title = None, report_id = None, user = None, original_polygon = None, zoning_code = None):
    filters = Q()

    if title:
        filters &= Q(title__icontains=title)

    if architectural_style:
        styles = []
        for style in architectural_style:
            styles.append(style.upper())
        filters &= Q(architectural_style__in=styles)

    if area_total_min is not None:
        filters &= Q(area_total__gte=area_total_min)
    if area_total_max is not None:
        filters &= Q(area_total__lte=area_total_max)

    if width_min is not None:
        filters &= Q(width__gte=width_min)
    if width_max is not None:
        filters &= Q(width__lte=width_max)

    if height_min is not None:
        filters &= Q(height__gte=height_min)
    if height_max is not None:
        filters &= Q(height__lte=height_max)

    if depth_min is not None:
        filters &= Q(depth__gte=depth_min)
    if depth_max is not None:
        filters &= Q(depth__lte=depth_max)

    if stories:
        filters &= Q(stories__in=stories)

    if cars_capacity:
        filters &= Q(cars_capacity__in=cars_capacity)

    if foundation:
        filters &= Q(foundation__name__in=foundation)

    if exterior_wall_type:
        filters &= Q(exterior_wall_type__name__in=exterior_wall_type)

    if garage_type:
        filters &= Q(garage_type__name__in=garage_type)

    if units:
        mapping = {
        'SINGLE FAMILY': 1,
        'DUPLEX': 2,
        'MULTI FAMILY': 3,
        'OTHER': 4
        }
        new_units = [mapping.get(item.upper(), 0) for item in units]
        filters &= Q(units__in=new_units)

    if bedrooms:
        filters &= applyBedBathFilters('bedrooms_count', bedrooms)

    if bathrooms:
        filters &= applyBedBathFilters('bathrooms_count', bathrooms)

    zoning_rules = applyZoningRules(request, address, original_polygon, zoning_code)
    if zoning_rules:
        filters &= Q(depth__lte=zoning_rules['depth'])
        filters &= Q(width__lte=zoning_rules['width'])
        filters &= Q(area_total__lte=zoning_rules['area'])

    plans = ArchitecturalPlan.objects.filter(filters).distinct()

    if report_id:
        report = Report.objects.get(id=report_id, user=user)
        report.architectural_plans.set(plans)
        report.save()

    plans_data = list(plans.values())
    return plans_data

def getArchitecturalPlansV2(request, address, architectural_style=None, area_total_min=None, area_total_max=None,
                           width_min=None, width_max=None, height_min=None, height_max=None, depth_min=None,
                           depth_max=None, stories=None, cars_capacity=None, foundation=None, exterior_wall_type=None,
                           garage_type=None, units=None, bedrooms=None, bathrooms=None, title=None, report_id=None,
                           user=None, original_polygon=None, zoning_code=None, page=1, per_page=20, apply_pagination=False):
    filters = Q()

    if title:
        filters &= Q(title__icontains=title)

    if architectural_style:
        styles = [style.upper() for style in architectural_style]
        filters &= Q(architectural_style__in=styles)

    if area_total_min is not None:
        filters &= Q(area_total__gte=area_total_min)
    if area_total_max is not None:
        filters &= Q(area_total__lte=area_total_max)

    if width_min is not None:
        filters &= Q(width__gte=width_min)
    if width_max is not None:
        filters &= Q(width__lte=width_max)

    if height_min is not None:
        filters &= Q(height__gte=height_min)
    if height_max is not None:
        filters &= Q(height__lte=height_max)

    if depth_min is not None:
        filters &= Q(depth__gte=depth_min)
    if depth_max is not None:
        filters &= Q(depth__lte=depth_max)

    if stories:
        filters &= Q(stories__in=stories)

    if cars_capacity:
        filters &= Q(cars_capacity__in=cars_capacity)

    if foundation:
        filters &= Q(foundation__name__in=foundation)

    if exterior_wall_type:
        filters &= Q(exterior_wall_type__name__in=exterior_wall_type)

    if garage_type:
        filters &= Q(garage_type__name__in=garage_type)

    if units:
        mapping = {
            'SINGLE FAMILY': 1,
            'DUPLEX': 2,
            'MULTI FAMILY': 3,
            'OTHER': 4
        }
        new_units = [mapping.get(item.upper(), 0) for item in units]
        filters &= Q(units__in=new_units)

    if bedrooms:
        filters &= applyBedBathFilters('bedrooms_count', bedrooms)

    if bathrooms:
        filters &= applyBedBathFilters('bathrooms_count', bathrooms)

    zoning_rules = applyZoningRules(request, address, original_polygon, zoning_code)
    if zoning_rules:
        filters &= Q(depth__lte=zoning_rules['depth'])
        filters &= Q(width__lte=zoning_rules['width'])
        filters &= Q(area_total__lte=zoning_rules['area'])

    # Get all matching plans
    all_plans = ArchitecturalPlan.objects.filter(filters).distinct().order_by('id')

    if apply_pagination:
        # Pagination
        paginator = Paginator(all_plans, per_page)
        page_obj = paginator.get_page(page)

        plans_data = list(page_obj.object_list.values())
        return {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'plans': plans_data
        }
    else:
        # Return all plans without pagination
        plans_data = list(all_plans.values())
        return {
            'current_page': 1,
            'total_pages': 1,
            'total_items': all_plans.count(),
            'plans': plans_data
        }