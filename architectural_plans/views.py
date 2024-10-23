import json
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from IQbackend.mixins.auth import LoginRequiredMixin
from architectural_plans.helpers import getArchitecturalPlans, getArchitecturalPlansV2
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin
from architectural_plans.models import FavoritePlan, ArchitecturalPlan
from zoning.gis.get_parcel_information import getParcelAddressFromId

class GetArchitecturalPlansView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title')
            address = data.get('address', None)
            parcel_id = data.get('parcel_id', None)
            if (parcel_id):
                city = data.get('city', None)
                county = data.get('county', None)
                if (city != None or county != None):
                    result = getParcelAddressFromId(parcel_id, city, county)
                    if result:
                        address = result
                    else:
                        return JsonResponse({'data': {}, 'message': 'To get data from parcel number, you need to give city and county as well.'}, status=404)
            report_id = data.get('report_id')
            architectural_style = data.get('architectural_style')
            area_total_min = data.get('area_total_min')
            area_total_max = data.get('area_total_max')
            width_min = data.get('width_min')
            width_max = data.get('width_max')
            height_min = data.get('height_min')
            height_max = data.get('height_max')
            depth_min = data.get('depth_min')
            depth_max = data.get('depth_max')
            stories = data.get('stories')
            cars_capacity = data.get('cars_capacity')
            foundation = data.get('foundation')
            exterior_wall_type = data.get('exterior_wall_type')
            garage_type = data.get('garage_type')
            units = data.get('units')
            bedrooms = data.get('bedrooms')
            bathrooms = data.get('bathrooms')
            page_number = data.get('page_number', 1)
            per_page = data.get('per_page', 20)

            plans_data = getArchitecturalPlansV2(request, address, architectural_style, area_total_min, area_total_max, width_min, width_max, height_min, height_max, depth_min, depth_max, stories, cars_capacity, foundation, exterior_wall_type, garage_type, units, bedrooms, bathrooms, title, report_id, request.user, None, None, page_number, per_page, True)
            pagination = {
                'current_page': plans_data['current_page'], 
                'total_pages': plans_data['total_pages'], 
                'total_items': plans_data['total_items']
                }

            return JsonResponse({'data': plans_data['plans'], 'pagination': pagination, 'message': 'Architectural plans fetched successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ListFavoritePlansView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def get(self, request):
        try:
            favorites = list(ArchitecturalPlan.objects.filter(
                favorited_by__user=request.user
            ).values())

            return JsonResponse(
                {'data' : favorites}, 
                status=200
            )
        
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )

class AddFavoritePlanView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            plan_id = data.get('architectural_plan')

            architectural_plan = get_object_or_404(
                ArchitecturalPlan, 
                id=plan_id
            )

            favorite, created = FavoritePlan.objects.get_or_create(
                user=request.user, 
                architectural_plan=architectural_plan
            )

            if created:
                return JsonResponse(
                    {'message': 'Plan added to favorites.'}, 
                    status=201
                )
            else:
                return JsonResponse(
                    {'message': 'Plan is already in favorites.'}, 
                    status=200
                )
            
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )

class RemoveFavoritePlanView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def delete(self, request):
        try:
            data = json.loads(request.body)
            plan_id = data.get('architectural_plan')
            
            architectural_plan = get_object_or_404(
                ArchitecturalPlan, 
                id=plan_id
            )

            favorite = FavoritePlan.objects.filter(
                user=request.user, 
                architectural_plan=architectural_plan
            ).first()

            if favorite:
                favorite.delete()
                return JsonResponse(
                    {'message': 'Plan removed from favorites.'}, 
                    status=200
                )
            
            else:
                return JsonResponse(
                    {'message': 'Plan was not in favorites.'}, 
                    status=400
                )
            
        except Exception as e:
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )