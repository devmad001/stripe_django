import json
from django.views import View
from users.models import Report
from django.http import JsonResponse
from IQbackend.helpers import processAddress
from cost_estimation.helpers import getPropertyInfo
from django.views.decorators.csrf import csrf_exempt
from IQbackend.mixins.auth import LoginRequiredMixin
from cost_estimation.data_types import ArchitecturalPlan,Comparable
from IQbackend.mixins.subscribed import SubscriptionRequiredMixin
from architectural_plans.models import ArchitecturalPlan as DjangoArchitecturalPlan
from cost_estimation.helpers import predictConstructionCostFromModel, calculateTotalConstructionCost,getComparablesObjsArrayFromZillow, getComparablesObjsArray, getKPI
from zoning.gis.get_parcel_information import getParcelAddressFromId

@csrf_exempt
def get_construction_cost(request):
    if request.method == 'POST':
        try:
            # Get the message from the POST data
            q_state = request.POST.get('q_state')
            q_county = request.POST.get('q_county')
            q_quality = request.POST.get('q_quality')
            q_story_count = request.POST.get('q_story_count')
            q_basement_type = request.POST.get('q_basement_type')
            q_area = request.POST.get('q_area')
            garage_area = request.POST.get('garage_area')
            basement_area = request.POST.get('basement_area')

            print("Q state: ", q_state)
            print("Q county: ", q_county)
            print("Q quality: ", q_quality)
            print("Q story count: ", q_story_count)
            print("Q basement: ", q_basement_type)
            print("Q area: ", q_area)
            print("G area: ", garage_area)
            print("B area: ", basement_area)

            # Convert string inputs to integers
            q_area = int(q_area)
            q_story_count = int(q_story_count)
            garage_area = int(garage_area)
            basement_area = int(basement_area)

            # Call your functions to predict and calculate construction cost
            sq_ft_cost = predictConstructionCostFromModel(q_state, q_county, q_area, q_quality, q_story_count, q_basement_type)
            total_construction_cost = calculateTotalConstructionCost(sq_ft_cost, q_area, garage_area, basement_area, 'finished')
            print('Total Construction Cost : ', total_construction_cost)
            print('Square feet cost  : ', sq_ft_cost)

            return JsonResponse({'Construction Cost': total_construction_cost, "Square Feet": sq_ft_cost})

        except ValueError:
            return JsonResponse({'error': 'Invalid input. Ensure all input values are numeric.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

class GetComparableSalesViews(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
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
            address = processAddress(request, address)
            architectural_plan_id = data.get('architectural_plan_id')

            plan = DjangoArchitecturalPlan.objects.get(id=architectural_plan_id)
            archi_plan = ArchitecturalPlan(plan.area_total, plan.bedrooms_count, plan.bathrooms_count, 
                                                plan.bathrooms_full_count, plan.bathrooms_half_count, plan.stories, 
                                                plan.area_first_floor, plan.area_second_floor, plan.area_third_floor, 
                                                plan.area_basement, plan.area_garage, plan.cars_capacity, 
                                                ', '.join([location.name for location in plan.garage_location.all()]), 
                                                ', '.join([type.name for type in plan.garage_type.all()]), plan.width, 
                                                plan.depth, plan.height, plan.units, plan.buy_url, plan.plan_number, 
                                                plan.title, plan.image_link, plan.architectural_style, 
                                                ', '.join([foundation.name for foundation in plan.foundation.all()]), 
                                                ', '.join([wall.name for wall in plan.exterior_wall_type.all()]))
            report_id = data.get('report_id')
            if not address:
                return JsonResponse({'error': 'Address is required'}, status=400)

            # attom_data, created = AttomData.objects.get_or_create(address=address['full_address'])
            report = Report.objects.get(id=report_id, user=request.user)

            # if not created and attom_data.comparable_sales:
            #     comparable_sales = attom_data.comparable_sales
            # else:
            street, city, state = address['street_address'], address['city'], address['state']
            
            # comparables = getComparablesObjsArray(street, city, state)
            query_prop_for_comp = Comparable('',0,archi_plan.area_total,archi_plan.bedrooms_n,archi_plan.bathrooms_full_n,\
                               archi_plan.bathrooms_half_n,archi_plan.story_n,2024,5000,archi_plan.area_garage,archi_plan.area_basement,\
                                0,archi_plan.area_basement,0,0)
            comparables = getComparablesObjsArrayFromZillow(street, city, state,query_prop_for_comp,address['lat'],address['lng'])
            
            if not comparables:
                return JsonResponse({'data': [], 'message': 'No comparables found.'}, status=404)

            comparable_sales = []
            for comp in comparables:
                comp.setZillowLink()
                comp_dict = {
                    'address': comp.address,
                    'distance': comp.distance,
                    'area': comp.area,
                    'bedroom_count': comp.bed_n,
                    'bathroom_count': comp.full_bath_n + comp.half_bath_n / 2,
                    'baths_full': comp.full_bath_n,
                    'baths_half': comp.half_bath_n,
                    'story_count': comp.story_n,
                    'year': comp.year,
                    'lot_area': comp.lot_area if comp.lot_area is not None else 0,
                    'price_per_sq_ft': comp.price_per_sq_ft,
                    'deeds_sale_amount': comp.deeds_sale_amount,
                    'has_fireplace': comp.has_fireplace,
                    'has_pool': comp.has_pool,
                    'zillow_link': comp.zillow_link
                }
                comparable_sales.append(comp_dict)

                # attom_data.comparable_sales = comparable_sales
                # attom_data.save()

            report.comparable_sales = comparable_sales
            report.save()

            return JsonResponse({'data': comparable_sales, 'message': 'Comparable sales fetched successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GetKPIsView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request):
      try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        build_quality = data.get('build_quality')
        land_acquisition_cost = data.get('land_acquisition_cost')
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
        address = processAddress(request, address)
        architectural_plan_id = data.get('architectural_plan_id')
        basement_type = data.get('basement_type','NO')
        walltype = data.get('walltype', 'Brick Veneer - Wood Frame')

        report = Report.objects.get(id=report_id, user=request.user)
        plan = DjangoArchitecturalPlan.objects.get(id=architectural_plan_id)
        architectural_plan = ArchitecturalPlan(plan.area_total, plan.bedrooms_count, plan.bathrooms_count, 
                                               plan.bathrooms_full_count, plan.bathrooms_half_count, plan.stories, 
                                               plan.area_first_floor, plan.area_second_floor, plan.area_third_floor, 
                                               plan.area_basement, plan.area_garage, plan.cars_capacity, 
                                               ', '.join([location.name for location in plan.garage_location.all()]), 
                                               ', '.join([type.name for type in plan.garage_type.all()]), plan.width, 
                                               plan.depth, plan.height, plan.units, plan.buy_url, plan.plan_number, 
                                               plan.title, plan.image_link, plan.architectural_style, 
                                               ', '.join([foundation.name for foundation in plan.foundation.all()]), 
                                               ', '.join([wall.name for wall in plan.exterior_wall_type.all()]))
        
        street, city, state = address['street_address'], address['city'], address['state']
        
        kpi = getKPI(architectural_plan, street, city, state, build_quality, basement_type, land_acquisition_cost, walltype)
        if not kpi:
            return JsonResponse({'data': {}, 'message': 'KPIs could not be calculated because no comparables found.'}, status=404)
        kpi.setLandAcquisitionCost(land_acquisition_cost)
        heated_area = architectural_plan.area_total
        unheated_area = architectural_plan.area_garage
        if(basement_type=='UNFINISHED'):
            unheated_area += architectural_plan.area_basement
        if(basement_type=='FINISHED'):
            heated_area += architectural_plan.area_basement
        kpi.setFinishedAndUnfinishedValues(heated_area,unheated_area)
        
        data = {
          'vac': kpi.vac_min,
          'construction_cost': kpi.construction_cost,
          'total_project_cost': kpi.total_project_cost,
          'equity': 0 if kpi.vac_min == 0 else kpi.equity_min,
          'area_heated' : kpi.area_finished,
          'area_unheated' : kpi.area_unfinished,
          'msacc_finished' : kpi.price_psqft_finished,
          'msacc_unfinished' : kpi.price_psqft_unfinished,
          'cost_finished' : kpi.construction_cost_finished,
          'cost_unfinished' : kpi.construction_cost_unfinished,
          'cost_extra' : kpi.construction_cost_extra,
          'acquisition_cost': report.acquisition_cost,
          'other_cost': report.other_cost
        }
        report.kpis = data
        report.selected_plan = plan
        report.save()

        return JsonResponse({'data': data, 'message': 'KPIs fetched successfully'}, status=200)
      except Exception as e:
          print(str(e))
          return JsonResponse({'error': str(e)}, status=500)

class GetPropertyInfoView(LoginRequiredMixin, SubscriptionRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address = data.get('address')
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
            address = processAddress(request, address)
            report_id = data.get('report_id')
            if not address:
                return JsonResponse({'error': 'Address is required'}, status=400)

            report = Report.objects.get(id=report_id, user=request.user)
            property_data = getPropertyInfo(address['full_address'], address['street_address'], address['city'], address['state'])

            if (property_data == None):
                return JsonResponse({'data': {}, 'message': 'No property information found.'}, status=404)

            report.property = property_data
            report.save()

            return JsonResponse({'data': property_data, 'message': 'Property information fetched successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
      