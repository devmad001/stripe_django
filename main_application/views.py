import re
import json
import math
import pickle
import datetime
import urllib.parse
import pandas as pd, numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# imports from refactored apis for demo endpoints

from authentication.helpers import store_session_data, get_session_data
from main_application.helper import dict_to_object
from chatbot.data_types import Property
from zoning.helpers import demo_getZoningObj
from ml_models.data.attom_api_data import attom_resp_json, attom_comp_resp_json
from zoning.gis.setback_calculations import getSetbackPolygon
from chatbot.input.address_processing import getMSANameForCounty
from main_application.data_types import plan_obj, comp_obj, userInputForm, queryPropertyForComps, KPI
from cost_estimation.helpers import predictConstructionCostFromModel, calculateTotalConstructionCost
from zoning.views import getFrontage, getFrontSetBack, getRearSetBack, getSideSetBack, getFar, getLotCoverage, getBuildingHeight

# @logout_inactive_user
def dashboard(request):
    return JsonResponse({'message': 'You are now on dashboard'}, status=201)

def municipality_dashboard(request):
    client_token = request.GET.get('token') 

    if client_token == request.session['client_token']:
        return JsonResponse({'message':'Allow Dashboard', 'flag':True}, status=200)
    else:
        return JsonResponse({'error': 'Not Allowed', 'flag':False}, status=400)


def callAppropriateSubFunction(request,user_txt):
    prompt = 'For the address,8226 E 34th St, Tulsa, OK'
    search_result = re.search("front setback", user_txt,re.IGNORECASE)
    print("----------Search reesults are here:", search_result)
    if(search_result!=None):
        print("----------Hiting again Search reesults are here:", search_result)

        ans = getFrontSetBack(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the front setback is '+str(ans)
        return prompt+ans_str

    search_result = re.search("rear setback", user_txt,re.IGNORECASE)
    if(search_result!=None):
        ans = getRearSetBack(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the rear setback is '+str(ans)
        return prompt+ans_str
    
    search_result = re.search("side setback", user_txt,re.IGNORECASE)
    if(search_result!=None):
        ans = getSideSetBack(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the side setback is '+str(ans)
        return prompt+ans_str
    
    search_result = re.search("far", user_txt,re.IGNORECASE)
    if(search_result!=None):
        ans = getFar(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the FAR is '+str(ans)
        return prompt+ans_str

    search_result = re.search("coverage", user_txt,re.IGNORECASE)
    if(search_result!=None):
        ans = getLotCoverage(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the coverage is '+str(ans)
        return prompt+ans_str

    search_result = re.search("height", user_txt,re.IGNORECASE)
    if(search_result!=None):
        ans = getBuildingHeight(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the building height is '+str(ans)
        return prompt+ans_str

    search_result = re.search("frontage", user_txt,re.IGNORECASE)
    if(search_result!=None):
        ans = getFrontage(dict_to_object(request.session['zoning_obj']))
        ans_str = ', the frontage is '+str(ans)
        return prompt+ans_str

    search_result = re.search("cost", user_txt,re.IGNORECASE)
    if(search_result!=None):
        propertyObj = dict_to_object(request.session['propertyObj'])
        sq_ft_cost = predictConstructionCostFromModel(propertyObj.p_state,propertyObj.p_county,\
                                                      'SILVER',1,'UNFINISHED',propertyObj.p_max_area_after_far)
        total_cost = calculateTotalConstructionCost(sq_ft_cost, propertyObj.p_max_area_after_far, 300,400,'UNFINISHED')
        ans_str = ', the per square feet construction cost is $'+str(sq_ft_cost)+\
                    '. To build '+str(propertyObj.p_max_area_after_far)+\
        ' square feet house with garage and basement, the total constrction cost will be $'+str(total_cost)
        return prompt+ans_str

    if(search_result==None):
        return 'Error : We are unable to get your query. Can you please repharase your query.Thanks!'
   

def callAppropriateSubFunctionLLM(request, coi,reqs_type):
    print(coi)
    zoning_obj = dict_to_object(request.session['zoning_obj'])

    print("--------------- callong here ---------", zoning_obj)
    

    prompt = ''
    search_result = re.search("front setback", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getFrontSetBack(zoning_obj)
        ans_str = ', the front setback is '+str(ans)
        return prompt+ans_str

    search_result = re.search("rear setback", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getRearSetBack(zoning_obj)
        ans_str = ', the rear setback is '+str(ans)
        return prompt+ans_str

    search_result = re.search("side setback", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getSideSetBack(zoning_obj)
        ans_str = ', the side setback is '+str(ans)
        return prompt+ans_str

    search_result = re.search("far", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getFar(zoning_obj)
        ans_str = ', the FAR is '+str(ans)
        return prompt+ans_str

    search_result = re.search("coverage", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getLotCoverage(zoning_obj)
        ans_str = ', the coverage is '+str(ans)
        return prompt+ans_str

    search_result = re.search("height", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getBuildingHeight(zoning_obj)
        ans_str = ', the building height is '+str(ans)
        return prompt+ans_str

    search_result = re.search("frontage", coi,re.IGNORECASE)
    if(search_result!=None):
        ans = getFrontage(zoning_obj)
        ans_str = ', the frontage is '+str(ans)
        return prompt+ans_str

    search_result = re.search("construction cost", coi,re.IGNORECASE)
    if(search_result!=None):
        propertyObj = dict_to_object(request.session['propertyObj'])
        print('Obj area val:',propertyObj.p_max_area_after_far)
        area_val = propertyObj.p_max_area_after_far
        potential_number = [int(i) for i in coi.split() if i.isdigit()]
        if(len(potential_number)>0 and potential_number[0]>500 and potential_number[0]<7500):
            area_val = potential_number[0]
            print('custom area val : ',area_val)
        sq_ft_cost = predictConstructionCostFromModel(propertyObj.p_state,propertyObj.p_county,\
                                                      'SILVER',1,'UNFINISHED',area_val)
        total_cost = calculateTotalConstructionCost(sq_ft_cost, area_val, 0,0,'UNFINISHED')
        ans_str = ', the per square feet construction cost is $'+str(sq_ft_cost)+\
                    '. To build '+str(area_val)+\
        ' square feet house with garage and basement, the total constrction cost will be $'+str(total_cost)
        return prompt+ans_str

    if(search_result==None):
        return 'Sorry, I am exclusively designed to assist you on land development questions. As such, I was unable to process your request. Could you please reformulate the information you are looking for ?'



def demo_callAttomPropertyAPI(addrs_part1,addrs_part2):
    addrs_part1_uri = urllib.parse.quote(addrs_part1)
    addrs_part2_uri = urllib.parse.quote(addrs_part2)
    print('Address Part1 : ',addrs_part1_uri,' Address Part2 : ',addrs_part2_uri)
    # attom_url = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/expandedprofile?address1='+addrs_part1_uri+'&address2='+addrs_part2_uri+'&debug=True'
    # headers = {'apikey': '69f2bfd055eeeff3dd1296afaba9106b','accept': "application/json", }
    # attom_resp = requests.get(attom_url,headers=headers)
    # attom_resp_json = attom_resp.json()
    return attom_resp_json


def demo_callAttomComparableAPI(address):
    comp_address = '8226 E 34TH ST'
    city = 'TULSA'
    state = 'OK'
    comp_address_uri_encoded = urllib.parse.quote(comp_address)
    # attom_comp_url = 'https://api.gateway.attomdata.com/property/v2/salescomparables/address/'+comp_address_uri_encoded+'/'+city+'/US/'+state+'/-'
    # headers = {'apikey': '69f2bfd055eeeff3dd1296afaba9106b','accept': "application/json", }
    # attom_comp_resp = requests.get(attom_comp_url,headers=headers)
    return attom_comp_resp_json



def demo_getPropObj(address):
    address_parts = address.split(',', 1)

    address_p1 = address_parts[0]
    address_p2 = address_parts[1]
    attom_resp_json = demo_callAttomPropertyAPI(address_p1,address_p2)
    p_cord = [[-95.884011,36.112993],[-95.884000,36.112657],[-95.884241,36.112651],[-95.884270,36.112980],[-95.884011,36.112993]]
    p_lat = float(attom_resp_json['property'][0]['location']['latitude']) if ('latitude' in attom_resp_json['property'][0]['location'] and attom_resp_json['property'][0]['location']['latitude'] is not None) else 0.0   
    p_lng = float(attom_resp_json['property'][0]['location']['longitude']) if ('longitude' in attom_resp_json['property'][0]['location'] and attom_resp_json['property'][0]['location']['longitude'] is not None) else 0.0
    p_area = attom_resp_json['property'][0]['lot']['lotSize2'] if ('lotSize2' in attom_resp_json['property'][0]['lot'] and attom_resp_json['property'][0]['lot']['lotSize2'] is not None) else 0.0
    p_tax_amount = attom_resp_json['property'][0]['assessment']['tax']['taxAmt']
    p_owner_name = attom_resp_json['property'][0]['assessment']['owner']['owner1']['fullName']
    p_zoning_classification = attom_resp_json['property'][0]['lot']['siteZoningIdent']
    p_zoning_dscrp = attom_resp_json['property'][0]['summary']['propClass']
    p_type = attom_resp_json['property'][0]['lot']['zoningType']
    p_county = attom_resp_json['property'][0]['area']['munName']
    p_state = attom_resp_json['property'][0]['address']['countrySubd']
    p_city = attom_resp_json['property'][0]['address']['locality']
    p_street_adr = attom_resp_json['property'][0]['address']['line1']
    p_parcel_id = attom_resp_json['property'][0]['identifier']['apn']
    p_query_address = attom_resp_json['property'][0]['address']['oneLine']
    

    propertyObj = Property(p_cord,p_lat,p_lng,p_area,'',p_tax_amount,\
                p_city,p_state,p_county,p_street_adr,p_query_address,p_parcel_id,\
                p_type,p_zoning_classification,p_zoning_dscrp,p_owner_name)

    return propertyObj

def demo_applyZoningRules(setback_front,setback_rear,setback_side,propertyObj):
    polygon_final,sides_after_zoning = getSetbackPolygon(propertyObj.p_cord, setback_front, setback_rear, setback_side)
    propertyObj.p_depth_after_zoning = sides_after_zoning[2][0]
    propertyObj.p_width_after_zoning = sides_after_zoning[0]
    # propertyObj.p_depth_after_zoning = 78
    # propertyObj.p_width_after_zoning = 64

def demo_calculatePropertyDimensions(propertyObj):
    propertyObj.p_depth = 122
    propertyObj.p_width = 76

def demo_getShortListedPlans(userInputObj,p_width,p_depth):
    plans_data = pd.read_csv('ml_models/data/architectural_plans/architectural_plans_preprocessed.csv')
    limited_plan_flag = False
    
    shortlisted_plans = plans_data.loc[(plans_data['area_total'] >= userInputObj.min_area) &\
                                        (plans_data['area_total'] <= userInputObj.max_area) &\
                                        (plans_data['bathrooms_count']==userInputObj.total_bath_count) &\
                                        (plans_data['bedrooms_count'] == userInputObj.bed_count) &\
                                        (plans_data['stories']==userInputObj.story_count) &\
                                        (plans_data['cars_capacity']==userInputObj.garage_count) &\
                                        (plans_data['area_basement']==0 if userInputObj.basement_type=='NO' \
                                         else plans_data['area_basement']>0 ) &\
                                        (plans_data['width'] <= p_width) &\
                                        (plans_data['depth'] <= p_depth) ]
    shortlisted_plans_n = len(shortlisted_plans)

    if(shortlisted_plans_n<5):
        shortlisted_plans = plans_data.loc[(plans_data['area_total'] >= userInputObj.min_area) & (plans_data['area_total'] <= userInputObj.max_area) &\
                                             (plans_data['width'] <= p_width) & (plans_data['depth'] <= p_depth) ]
        limited_plan_flag = True

    shortlisted_plans_n = len(shortlisted_plans)
    shortlisted_plans_arr = []
    max_plans_to_show_n = 10
    if(shortlisted_plans_n>max_plans_to_show_n):
        shortlisted_plans_n = max_plans_to_show_n

    for idx in range(shortlisted_plans_n):
        plan = shortlisted_plans.iloc[idx]
        shortlisted_plans_arr.append(plan_obj(plan.iloc[0],plan.iloc[1],plan.iloc[2],plan.iloc[3],\
                     plan.iloc[4],plan.iloc[5],plan.iloc[6],plan.iloc[7],\
                     plan.iloc[8],plan.iloc[9],plan.iloc[10],plan.iloc[11],plan.iloc[12],plan.iloc[13],\
                     plan.iloc[14],plan.iloc[15],plan.iloc[16],plan.iloc[17]))
    return shortlisted_plans_arr,limited_plan_flag


def get_userChoices(propertyObj,min_area,max_area,bed_count,full_bath_count,story_count,build_quality,acquisition_cost):

    # min_area = 5000
    # max_area = propertyObj.p_max_area_after_far
    # bed_count = 3
    # full_bath_count = 2
    half_bath_count = 0
    total_bath_count = full_bath_count + 0.5*half_bath_count
    # story_count = 1
    garage_count = 1
    # build_quality = 'BRONZE'
    basement_type = 'UNFINISHED'
    # acquisition_cost = 75000
    home_style = ''
    complete_address = propertyObj.p_query_address
    userInputObj = userInputForm(min_area,max_area,bed_count,full_bath_count,half_bath_count,story_count,garage_count,\
                 build_quality,basement_type,acquisition_cost,home_style,complete_address)
    return userInputObj

def demo_getSelectedPlanIdx(shortlisted_plans_arr, selectedPlanName):
    for idx,plan in enumerate(shortlisted_plans_arr):
        if(shortlisted_plans_arr[idx].plan_number == selectedPlanName):
            return idx

def demo_initializeQueryPropertyFromSelectedArchitectural(selectedPlan):
    today = datetime.date.today()
    q_year = today.year
    q_area = selectedPlan.area_total
    q_area_basement = selectedPlan.area_basement
    q_area_garage = selectedPlan.area_garage
    q_baths_full = selectedPlan.bathrooms_full_count
    q_baths_half = selectedPlan.bathrooms_half_count
    q_bedrooms = selectedPlan.bedrooms_count
    queryPropertyObj = queryPropertyForComps(q_year,q_area,q_area_basement,q_area_garage,q_baths_full,q_baths_half,q_bedrooms)
    return queryPropertyObj

def demo_getComparablesObjsArray(address):

    attom_comp_resp = demo_callAttomComparableAPI(address)
    comps_received_n = len(attom_comp_resp['RESPONSE_GROUP']['RESPONSE']['RESPONSE_DATA']['PROPERTY_INFORMATION_RESPONSE_ext']['SUBJECT_PROPERTY_ext']['PROPERTY'])
    cmp_items_arr = []
    
    for i in range(comps_received_n):
        if(i>0):
            cmp_i = attom_comp_resp['RESPONSE_GROUP']['RESPONSE']['RESPONSE_DATA']\
                                ['PROPERTY_INFORMATION_RESPONSE_ext']['SUBJECT_PROPERTY_ext']['PROPERTY'][i]
            cmp_price_per_sq_ft = float(cmp_i['COMPARABLE_PROPERTY_ext']['SALES_HISTORY']['@PricePerSquareFootAmount'])
            cmp_deeds_sale_amount = float(cmp_i['COMPARABLE_PROPERTY_ext']['SALES_HISTORY']['@PropertySalesAmount'])
            cmp_area = float(cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@GrossLivingAreaSquareFeetCount'])
            cmp_lot_size = float(cmp_i['COMPARABLE_PROPERTY_ext']['SITE']['@LotSquareFeetCount'])
            cmp_bedroom_count = int(cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBedroomCount'])
            cmp_baths_total = 0 if cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBathroomCount'] == '' \
                                else float(cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBathroomCount'])
            cmp_baths_half = 0 if cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBathroomHalfCount_ext'] == '' \
                                else int(cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBathroomHalfCount_ext'])
            cmp_baths_full = 0 if cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBathroomFullCount_ext'] == '' \
                                else int(cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['@TotalBathroomFullCount_ext'])
            cmp_year_build = int(cmp_i['COMPARABLE_PROPERTY_ext']['STRUCTURE']['STRUCTURE_ANALYSIS']\
                                 ['@PropertyStructureBuiltYear'])
            cmp_distance = float(cmp_i['COMPARABLE_PROPERTY_ext']['@DistanceFromSubjectPropertyMilesCount'])
            cmp_address = cmp_i['COMPARABLE_PROPERTY_ext']['@_StreetAddress']+','+\
                        cmp_i['COMPARABLE_PROPERTY_ext']['@_City']+','+cmp_i['COMPARABLE_PROPERTY_ext']['@_State']

            cmp_items_arr.append(comp_obj(cmp_address,cmp_distance,cmp_area,cmp_bedroom_count,cmp_baths_total,\
                                          cmp_year_build,cmp_lot_size,cmp_deeds_sale_amount,\
                                          cmp_price_per_sq_ft,cmp_deeds_sale_amount))
    if(len(cmp_items_arr)<3):
        return False
    return cmp_items_arr


def demo_adjustComparablePrice(query_property,comparable_property):
    q_year_build = query_property.year_build
    q_area = query_property.area
    q_baths_full = query_property.baths_full
    q_baths_half = query_property.baths_half
    q_bedrooms = query_property.bedrooms

    cmp_avm = comparable_property.deeds_sale_amount
    cmp_year_build = comparable_property.year
    cmp_area = comparable_property.area
    cmp_price_per_sq_ft = comparable_property.price_per_sq_ft
    cmp_baths_total = comparable_property.bath_count
    cmp_baths_half,cmp_baths_full = math.modf(cmp_baths_total)
    cmp_baths_half =  cmp_baths_half *2
    cmp_lot_size = comparable_property.lot_area
    cmp_bedroom_count = comparable_property.bed_count

    diff_year = cmp_year_build - q_year_build
    diff_area = cmp_area - q_area
    diff_bath_full = int(cmp_baths_full - q_baths_full)
    diff_bath_half = int(cmp_baths_half - q_baths_half)
    adj_price = cmp_avm
    
    if(abs(diff_year)>=71):
        a_1 = cmp_avm*.15
    elif(abs(diff_year)>=41 & abs(diff_year)<=70):
        a_1 = cmp_avm*.1
    elif(abs(diff_year)>=21 & abs(diff_year)<=40):
        a_1 = cmp_avm*.05
    else:
        a_1 = 0
    if(diff_year<0):
        adj_price = adj_price + a_1
    else:
        adj_price = adj_price - a_1
    
    # print('Comp Price after year adj : ',adj_price)
    
    a_2 = abs(diff_area) * cmp_price_per_sq_ft
    if(diff_area<0):
        adj_price = adj_price + a_2
    else:
        adj_price = adj_price - a_2
    
    # print('Comp Price after area adj : ',adj_price)
    
    half_bath_base_price = 4000
    alpha_bh = 200
    
    if(diff_bath_half==0):
        if(diff_year<0):
            adj_price = adj_price + (abs(diff_year/10)*alpha_bh)
        else:
            adj_price = adj_price - (abs(diff_year/10)*alpha_bh)
    
    if(diff_bath_half!=0):
        if((diff_year<0) & (diff_bath_half<0)):
            adj_price = adj_price + abs(diff_bath_half)*half_bath_base_price + (abs(diff_year/10)*alpha_bh)
        if((diff_year<0) & (diff_bath_half>0)):
            adj_price = adj_price - (abs(diff_bath_half)*half_bath_base_price - (abs(diff_year/10)*alpha_bh))
        if((diff_year>0) & (diff_bath_half<0)):
            adj_price = adj_price + abs(diff_bath_half)*half_bath_base_price - (abs(diff_year/10)*alpha_bh)
        if((diff_year>0) & (diff_bath_half>0)):
            adj_price = adj_price - abs(diff_bath_half)*half_bath_base_price - (abs(diff_year/10)*alpha_bh)
    
    # print('Comp Price after half bath adj : ',adj_price)
    
    full_bath_base_price = 8000
    alpha_bf = 400
    
    if(diff_bath_full==0):
        if(diff_year<0):
            adj_price = adj_price + (abs(diff_year/10)*alpha_bf)
        else:
            adj_price = adj_price - (abs(diff_year/10)*alpha_bf)
    
    if(diff_bath_full!=0):
        if((diff_year<0) & (diff_bath_full<0)):
            adj_price = adj_price + abs(diff_bath_full)*full_bath_base_price + (abs(diff_year/10)*alpha_bf)
        if((diff_year<0) & (diff_bath_full>0)):
            adj_price = adj_price - (abs(diff_bath_full)*full_bath_base_price - (abs(diff_year/10)*alpha_bf))
        if((diff_year>0) & (diff_bath_full<0)):
            adj_price = adj_price + abs(diff_bath_full)*full_bath_base_price - (abs(diff_year/10)*alpha_bf)
        if((diff_year>0) & (diff_bath_full>0)):
            adj_price = adj_price - abs(diff_bath_full)*full_bath_base_price - (abs(diff_year/10)*alpha_bf)

    return adj_price


def demo_setAndGetAdjustedValuesofComparables(cmp_items_arr,query_prop):
    comparables_adjst_prices = [demo_adjustComparablePrice(query_prop,cmp_item) for cmp_item in cmp_items_arr]
    for idx,cmp_item in enumerate(cmp_items_arr):
        cmp_item.setZillowLink()
        cmp_item.setValue(comparables_adjst_prices[idx])
        # cmp_item.print()
    return comparables_adjst_prices

def demo_setVACofQueryPropertyObj(query_prop,cmp_items_arr,comparables_adjst_prices):
    sorted_comps_idx=np.argsort(comparables_adjst_prices)
    cmps_arr_n = len(sorted_comps_idx)
    mid_idx = int(np.floor(cmps_arr_n/2))
    mid_comps_adjst_prices = cmp_items_arr[sorted_comps_idx[mid_idx]].value
    q_vac = int(np.mean(comparables_adjst_prices))
    q_vac2 = int(np.mean(mid_comps_adjst_prices))
    query_prop.setVAC(q_vac)
    query_prop.setVAC2(q_vac2)


def demo_getMSANameForCounty(county_name, state_name):
    county_name = county_name.upper().strip()
    state_name = state_name.upper().strip()
    data_path = 'ml_models/models/cost_model/mapping_files/'
    county_to_msa_file =  pd.read_csv(data_path+'county_to_msa_mapping.csv')
    state_county_cmb = state_name+','+county_name
    for msa_name,state_county_val in zip(county_to_msa_file['MSA'],	county_to_msa_file['State_county']):
        if(state_county_cmb == state_county_val):
            return msa_name
    return False
    

def demo_predictConstructionCostFromModel(q_state,q_county,q_quality,q_story_count,q_basement_type,q_area):
    dir_name = 'ml_models/models/cost_model/mapping_files/'
    q_state = q_state.upper()
    q_county = q_county.upper()
    q_quality = q_quality.upper()
    q_basement_type = q_basement_type.upper()

    if(q_area>5000):
        q_area = 5000
    if(q_area<1000):
        q_area = 1000

    q_city = getMSANameForCounty(q_county, q_state)

    if(q_city==False):
        return False

    state_city_mapping_file =  pd.read_csv(dir_name+'state_city_mapping.csv')
    state_city_dict = {}
    for state_city_name,state_city_mapping in zip(state_city_mapping_file['State_city'],state_city_mapping_file['Mapping']):
        state_city_dict[state_city_name] = state_city_mapping

    quality_mapping_file =  pd.read_csv(dir_name+'quality_mapping.csv')
    quality_val_dict = {}
    for quality_name,quality_mapping in zip(quality_mapping_file['Quality'],quality_mapping_file['Mapping']):
        quality_val_dict[quality_name] = quality_mapping

    basement_mapping_file =  pd.read_csv(dir_name+'basement_mapping.csv')
    basement_val_dict = {}
    for basement_name,basement_mapping in zip(basement_mapping_file['Basement'],basement_mapping_file['Mapping']):
        basement_val_dict[basement_name] = basement_mapping

    user_input = [q_state,q_city,q_quality,q_story_count,'NO',q_area]
    user_input_merged = [user_input[0]+','+user_input[1],user_input[2],user_input[3],user_input[4],user_input[5]]
    user_input_numeric = [[quality_val_dict[user_input_merged[1]],\
                     user_input_merged[2],basement_val_dict[user_input_merged[3]],user_input_merged[4]]]
    
    model_id = state_city_dict[user_input_merged[0]]
    pred_model = pickle.load(open('ml_models/models/state_wise_models/prediction_model_'+str(model_id)+'.sav', 'rb'))
    per_sq_ft_cost = pred_model.predict(user_input_numeric)
    
    return round(per_sq_ft_cost[0],2)
    

def demo_calculateTotalConstructionCost(sq_ft_cost, area, area_basement,area_garage, basement_type, unfinished_scaling_factor=0.55):
    total_construction_cost = sq_ft_cost * area + area_garage*sq_ft_cost*unfinished_scaling_factor
    basement_type = basement_type.upper()
    if(basement_type=='FINISHED'):
        total_construction_cost += area_basement*sq_ft_cost
    if(basement_type=='UNFINISHED'):
        total_construction_cost += area_basement*sq_ft_cost*unfinished_scaling_factor
    return int(total_construction_cost)


def demo_convertPlanDictToPlanObj(selected_plan_dict):
    planObj = plan_obj(selected_plan_dict['area_total'],selected_plan_dict['bedrooms_count'],\
                       selected_plan_dict['bathrooms_count'],selected_plan_dict['bathrooms_full_count'],\
                       selected_plan_dict['bathrooms_half_count'],selected_plan_dict['stories'],\
                       selected_plan_dict['area_first_floor'],selected_plan_dict['area_second_floor'],\
                       selected_plan_dict['area_third_floor'],selected_plan_dict['area_basement'],\
                       selected_plan_dict['area_garage'],selected_plan_dict['cars_capacity'],\
                       selected_plan_dict['width'],selected_plan_dict['depth'],selected_plan_dict['buy_url'],\
                       selected_plan_dict['plan_number'],selected_plan_dict['title'],\
                       selected_plan_dict['image_link'])
    return planObj

def demo_convertComparableDictToComparableObj(comparable_dict):
    comparableObj = comp_obj(comparable_dict['address'],comparable_dict['distance'],\
                            comparable_dict['area'],comparable_dict['bed_count'],\
                            comparable_dict['bath_count'],comparable_dict['year'],\
                            comparable_dict['lot_area'],comparable_dict['avm'],\
                            comparable_dict['price_per_sq_ft'],comparable_dict['deeds_sale_amount'])
    return comparableObj

@csrf_exempt
def demo_populateDashBoard(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        build_quality = data.get('build_quality')
        story_count = data.get('story_count')
        bed_count = data.get('bed_count')
        bath_count = data.get('bath_count')
        min_area = data.get('min_area')
        max_area = data.get('max_area')
        acquisition_cost = data.get('acquisition_cost')
        # build_quality = 'BRONZE'
        # story_count=1
        basement_type = 'UNFINISHED'

        demo_propObj = demo_getPropObj('8226 E 34th St, Tulsa, OK')
        demo_zoneObj = demo_getZoningObj('RS3','Tulsa','OK')
        demo_propObj.setMaxAreaAfterFar(demo_zoneObj.zoning_far)
        
        demo_userChoices = get_userChoices(demo_propObj,min_area,max_area,bed_count,\
                                           bath_count,story_count,build_quality,acquisition_cost)
        demo_calculatePropertyDimensions(demo_propObj)
        demo_applyZoningRules(demo_zoneObj.zoning_min_front_setback,demo_zoneObj.zoning_min_rear_setback,\
                            demo_zoneObj.zoning_min_side_setback,demo_propObj)
        
        # return JsonResponse({"api_resp": 'P1'})
        demo_shortListedPlans,flag = demo_getShortListedPlans(demo_userChoices,demo_propObj.p_width_after_zoning,\
                                                        demo_propObj.p_depth_after_zoning)
        # return JsonResponse({"api_resp": 'P1'})
        demo_selectedPlanIdx = demo_getSelectedPlanIdx(demo_shortListedPlans, demo_shortListedPlans[0].plan_number)
        # return JsonResponse({"api_resp": 'P1'})
        demo_queryPropObj = demo_initializeQueryPropertyFromSelectedArchitectural(demo_shortListedPlans[demo_selectedPlanIdx])
        # return JsonResponse({"api_resp": 'P1'})
        cmp_items_arr = demo_getComparablesObjsArray('')
        # return JsonResponse({"api_resp": 'P1'})
        comparables_adjst_prices = demo_setAndGetAdjustedValuesofComparables(cmp_items_arr,demo_queryPropObj)
        demo_setVACofQueryPropertyObj(demo_queryPropObj,cmp_items_arr,comparables_adjst_prices)

        demo_userChoices.addr_county = demo_propObj.p_county
        demo_userChoices.addr_city = demo_propObj.p_city 
        demo_userChoices.addr_state = demo_propObj.p_state
        print('County Name : ',demo_userChoices.addr_county)
        # return JsonResponse({"api_resp": 'P1'})


        MSACC = predictConstructionCostFromModel(demo_userChoices.addr_state,demo_userChoices.addr_county,\
                                                build_quality,story_count,basement_type,demo_queryPropObj.area)

        print('Per Sq Ft Cost :$',MSACC)

        total_construction_cost = calculateTotalConstructionCost(MSACC, demo_queryPropObj.area, demo_queryPropObj.area_basement,\
                                                                demo_queryPropObj.area_garage, basement_type, 0.55)

        print('Total Construction Cost : ',total_construction_cost)

        kpiObj = KPI(demo_queryPropObj.vac,demo_queryPropObj.vac2,total_construction_cost,demo_userChoices.acquisition_cost,MSACC)
        kpiObj.setVACbasedonQuality(demo_queryPropObj.vac,demo_queryPropObj.vac2,build_quality)
        kpi_dict = vars(kpiObj)
        api_resp = {}

        plans_dict_arr = [vars(x) for x in demo_shortListedPlans]

        selectedPlan = demo_shortListedPlans[demo_selectedPlanIdx]
        selectedPlan_dict = vars(selectedPlan)

        cmp_items_dict_arr = [vars(x) for x in cmp_items_arr]

        store_session_data(request, vars(demo_propObj), vars(demo_zoneObj), vars(demo_userChoices), vars(demo_queryPropObj), kpi_dict, plans_dict_arr, selectedPlan_dict, cmp_items_dict_arr)
        # request.session['dash_demo_propertyObj'] = vars(demo_propObj)
        # request.session['dash_demo_zoningObj'] = vars(demo_zoneObj)
        # request.session['dash_demo_userChoicesObj'] = vars(demo_userChoices)
        # request.session['dash_demo_queryPropObj'] = vars(demo_queryPropObj)
        # request.session['dash_demo_KPIObj'] = kpi_dict
        # request.session['demo_archi_plans'] = plans_dict_arr
        # request.session['demo_selected_archi_plan'] = selectedPlan_dict
        # request.session['demo_comparables'] = cmp_items_dict_arr

        api_resp['KPI_vals'] = kpi_dict
        api_resp['zoning_info'] = vars(demo_zoneObj)
        api_resp['archi_plans'] = plans_dict_arr
        api_resp['selected_archi_plan'] = selectedPlan_dict
        return JsonResponse({"api_resp": api_resp})

# def demo_populateZoningSection(request):
#     return JsonResponse({"api_resp": request.session['dash_demo_zoningObj']})

def demo_populatePropertyInfoSection(request):
    data = get_session_data(request, 'property')
    return JsonResponse({"api_resp": data['property']})

@csrf_exempt
def demo_change_buildQuality(request):
    if request.method == 'POST':
        #user_input = request.POST.get('user_message')
        data = json.loads(request.body)
        build_quality = data.get('build_quality')
        print(build_quality)

        kpi_dict = request.session['dash_demo_KPIObj']

        userChoices_dict = request.session['dash_demo_userChoicesObj']
        addr_state = userChoices_dict['addr_state']
        addr_city = userChoices_dict['addr_city']
        addr_county = userChoices_dict['addr_county']
        print('County Name :',addr_county)
        story_count = userChoices_dict['story_count']
        basement_type = userChoices_dict['basement_type']
        # build_quality = session[email_address][user_input_idx]['user_input']['build_quality']

        request.session['dash_demo_userChoicesObj'].update({'build_quality':build_quality})
        # session.modified = True

        query_prop_dict = request.session['dash_demo_queryPropObj']
        area = query_prop_dict['area']
        area_basement = query_prop_dict['area_basement']
        area_garage = query_prop_dict['area_garage']
        query_prop_vac = query_prop_dict['vac']
        query_prop_vac2 = query_prop_dict['vac2']
        
        # MSACC = predictConstructionCostFromModel(addr_state,addr_city,build_quality,story_count,basement_type,area)
        MSACC = predictConstructionCostFromModel(addr_state,addr_county,build_quality,story_count,basement_type,area)
        # MSACC = MSACC*0.95
        total_construction_cost = calculateTotalConstructionCost(MSACC, area, area_basement,\
                                                                area_garage, basement_type, 0.55)
        
        changedKPIObj = KPI(query_prop_vac,query_prop_vac2,total_construction_cost,\
                        kpi_dict['acquisition_cost'],MSACC)
        changedKPIObj.setVACbasedonQuality(query_prop_vac,query_prop_vac2,build_quality)
        changedKPIObj_dict = vars(changedKPIObj)
        request.session['dash_demo_KPIObj'] = changedKPIObj_dict


        return JsonResponse({"api_resp": changedKPIObj_dict})


@csrf_exempt
def demo_change_ArchitecturalPlan(request):
    if request.method == 'POST':
        #user_input = request.POST.get('user_message')
        data = json.loads(request.body)
        plan_number = data.get('plan_number')
        print('Requested plan :',plan_number)
        plan_count = len(request.session['demo_archi_plans'])
        print('Plans in session :',plan_count)

        for i in range(plan_count):
            if(request.session['demo_archi_plans'][i]['plan_number'] == plan_number):
                selected_plan_dict = request.session['demo_archi_plans'][i]
            # print(selected_plan_dict)

        selectedPlanObj = demo_convertPlanDictToPlanObj(selected_plan_dict)

        new_cmp_items_arr = [demo_convertComparableDictToComparableObj(comparable_dict) 
                         for comparable_dict in request.session['demo_comparables']]
        new_query_prop = demo_initializeQueryPropertyFromSelectedArchitectural(selectedPlanObj)

        new_comparables_adjst_prices = demo_setAndGetAdjustedValuesofComparables(new_cmp_items_arr,new_query_prop)
        demo_setVACofQueryPropertyObj(new_query_prop,new_cmp_items_arr,new_comparables_adjst_prices)

        new_cmp_items_dict_arr = [vars(x) for x in new_cmp_items_arr]
        request.session['demo_comparables'] = new_cmp_items_dict_arr

        request.session['dash_demo_queryPropObj'] = vars(new_query_prop)

        addr_state = request.session['dash_demo_userChoicesObj']['addr_state']
        addr_city = request.session['dash_demo_userChoicesObj']['addr_city']
        addr_county = request.session['dash_demo_userChoicesObj']['addr_county']
        print('County Name :',addr_county)
        story_count = request.session['dash_demo_userChoicesObj']['story_count']
        basement_type = request.session['dash_demo_userChoicesObj']['basement_type']
        build_quality = request.session['dash_demo_userChoicesObj']['build_quality']

        area = new_query_prop.area
        area_basement = new_query_prop.area_basement
        area_garage = new_query_prop.area_garage

        # MSACC = predictConstructionCostFromModel(addr_state,addr_city,build_quality,story_count,basement_type,area)
        MSACC = predictConstructionCostFromModel(addr_state,addr_county,build_quality,story_count,basement_type,area)
        
        total_construction_cost = calculateTotalConstructionCost(MSACC, area, area_basement,\
                                                                area_garage, basement_type, 0.55)

        changedKPIObj = KPI(new_query_prop.vac,new_query_prop.vac2,total_construction_cost,\
                      request.session['dash_demo_KPIObj']['acquisition_cost'],MSACC)
    
    
        changedKPIObj.setVACbasedonQuality(new_query_prop.vac,new_query_prop.vac2,build_quality)
        changedKPIObj_dict = vars(changedKPIObj)
        request.session['dash_demo_KPIObj'] = changedKPIObj_dict

        return JsonResponse({"api_resp": changedKPIObj_dict})


def demo_getSession(request):
    api_resp = {}
    # api_resp['dash_demo_propertyObj'] = request.session['dash_demo_propertyObj']
    # api_resp['dash_demo_zoningObj'] = request.session['dash_demo_zoningObj']
    # api_resp['dash_demo_userChoicesObj'] = request.session['dash_demo_userChoicesObj']
    # api_resp['dash_demo_queryPropObj'] = request.session['dash_demo_queryPropObj']
    # api_resp['dash_demo_KPIObj'] = request.session['dash_demo_KPIObj']
    # api_resp['session_data'] = request.session
    flag = False
    if 'dash_demo_KPIObj' in request.session.keys():
        flag = True
    return JsonResponse({"api_resp": flag})

################### **** DASHBOARD DEMO CODE ENDS HERE **** ##########################
################################################################################################
