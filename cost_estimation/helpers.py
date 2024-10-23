import urllib
import requests
import pandas as pd
import numpy as np
import xgboost as xg 
import pickle
import math
from django.conf import settings
from xgboost import XGBClassifier
from .data_types import KPI,Comparable,ArchitecturalPlan,Property
from architectural_plans.helpers import getArchitecturalPlans
from IQbackend.helpers import validateAddress
from cost_estimation.models import AttomData

from math import radians
from sklearn.metrics.pairwise import haversine_distances
import heapq

def getMSANameForCounty(county_name, state_name):
    '''
    Function gives Metropolitan statistical area (MSA) for a given county in a given state
 
    Parameters
    ----------
    county_name : string
    state_name : string
 
    Returns
    -------
    msa_name : string
        MSA in which the county lies in.
    '''
    dir_name = './ml_models/models/cost_model/mapping_files/'
    county_name = county_name.upper().strip()
    state_name = state_name.upper().strip()
    county_to_msa_file =  pd.read_csv(dir_name+'county_to_msa_mapping.csv')
    state_county_cmb = state_name+','+county_name
    for msa_name,state_county_val in zip(county_to_msa_file['MSA'],	county_to_msa_file['State_county']):
        if(state_county_cmb == state_county_val):
            return msa_name
    return False

def getQualityMapping(quality):

    '''
    Function gives numeric mapping {0,1,2} for quality {BRONZE,SILVER,GOLD}
 
    Parameters
    ----------
    quality : string
 
    Returns
    -------
    quality_mapping : int
        numeric mapping of quality value.
    '''

    dir_name = './ml_models/models/cost_model/mapping_files/'
    quality_mapping_file =  pd.read_csv(dir_name+'quality_mapping.csv')
    quality_val_dict = {}
    for quality_name,quality_mapping in zip(quality_mapping_file['Quality'],quality_mapping_file['Mapping']):
        quality_val_dict[quality_name] = quality_mapping
    return quality_val_dict[quality.upper()]

def getBasementMapping(basement):

    '''
    Function gives numeric mapping {0,1,2} for basement {NO,UNFINISHED,FINISHED}
 
    Parameters
    ----------
    basement : string
 
    Returns
    -------
    basement_mapping : int
        numeric mapping of basement value.
    '''

    dir_name = './ml_models/models/cost_model/mapping_files/'
    basement_mapping_file =  pd.read_csv(dir_name+'basement_mapping.csv')
    basement_val_dict = {}
    for basement_name,basement_mapping in zip(basement_mapping_file['Basement'],basement_mapping_file['Mapping']):
        basement_val_dict[basement_name] = basement_mapping
    return basement_val_dict[basement]


def getWallTypeMapping(walltype):

    '''
    Function gives numeric mapping {0,..,7} for wall types
 
    Parameters
    ----------
    walltype : string
 
    Returns
    -------
    walltype_mapping : int
        numeric mapping of walltype name.
    '''

    dir_name = './ml_models/models/cost_model/mapping_files/'
    walltype_mapping_file =  pd.read_csv(dir_name+'wall_type_mapping.csv')
    walltype_val_dict = {}
    for walltype_name,walltype_mapping in zip(walltype_mapping_file['Wall_Type'],walltype_mapping_file['Mapping']):
        walltype_val_dict[walltype_name] = walltype_mapping
    return walltype_val_dict[walltype]


def getStateCountyMapping(state,county):

    '''
    Function gives numeric mapping for combination of state and county {state','county}
 
    Parameters
    ----------
    state : string as abbreviation for example 'GA'
    county : string
 
    Returns
    -------
    state_county : int
        numeric mapping of state_county value.
    '''

    dir_name = './ml_models/models/cost_model/mapping_files/'
    state_county_mapping_file =  pd.read_csv(dir_name+'state_city_mapping.csv')
    state_county_dict = {}
    for state_county_name,state_county_mapping in zip(state_county_mapping_file['State_city'],state_county_mapping_file['Mapping']):
        state_county_dict[state_county_name] = state_county_mapping
    return state_county_dict[state+','+county]


def getMeanEncodingForStateCounty(state_county_mapping):

    '''
    Function gives numeric mean encoding value for the mapping value of state and county as {int}
 
    Parameters
    ----------
    state_county_mapping : int
 
    Returns
    -------
    state_county_mean_encoding : double
        mean encoding value of state_county value.
    '''

    dir_name = './ml_models/models/cost_model/mapping_files/'
    mean_encoding_mapping_file =  pd.read_csv(dir_name+'msacc_mean_encoding_24_q2.csv')
    mean_encoding_dict = {}
    for state_city_name,mean_encoding in zip(mean_encoding_mapping_file['state_city'],mean_encoding_mapping_file['mean_value']):
        mean_encoding_dict[state_city_name] = mean_encoding
    return mean_encoding_dict[state_county_mapping]

def getAddonCost(state,build_quality):

    '''
    Function gives add-on costs for a given state and build quality
 
    Parameters
    ----------
    state : string (state name as two digit abbreviation)
    build_quality : int (numeric mapping)
 
    Returns
    -------
    addonDict : dict
        a dictionary containing addon prices for various addon items.
    '''
    
    dir_name = './ml_models/data/cost_addon_data/'
    addOnCost = pd.read_csv(dir_name+'addon_cost.csv')
    addOns = np.array(addOnCost.loc[(addOnCost['State']==state) & (addOnCost['Quality']==build_quality)])
    addonDict = {}
    addonDict['kitchen'] = addOns[0][2]
    addonDict['bath_half'] = addOns[0][3]
    addonDict['bath_full'] = addOns[0][4]
    addonDict['entry_exit'] = addOns[0][5]
    addonDict['heating'] = addOns[0][6]
    addonDict['electric'] = addOns[0][7]
    addonDict['garage_attached_1_car'] = addOns[0][8]
    addonDict['garage_detached_1_car'] = addOns[0][9]
    addonDict['garage_attached_2_car'] = addOns[0][10]
    addonDict['garage_detached_2_car'] = addOns[0][11]
    return addonDict

def getOneHotEncoding(value,value_n):
    one_hot_rep = np.zeros((value.size, value_n))
    one_hot_rep[np.arange(value.size), value] = 1
    return one_hot_rep

def getPredictionModel(model_name='LR'):
    model_path = 'cost_estimation_model' 
    if(model_name=='XGB'):
        cost_model = xg.XGBRegressor()
        cost_model.load_model("./ml_models/models/cost_estimation_model/xgb_model_tuned_24_q2_1_hot")
    if(model_name =='LR'):
        cost_model = pickle.load(open('./ml_models/models/cost_estimation_model/lr_model_24_q2.sav', 'rb'))
    return cost_model

def predictConstructionCostFromModel(state, county, build_area, build_quality='BRONZE',story_n = 1,basement_type='NO',walltype='Brick Veneer - Wood Frame'):
    state = state.upper()
    county = county.upper()
    build_quality = build_quality.upper()
    basement_type = basement_type.upper()

    if(build_area>5000):
        build_area = 5000
    if(build_area<1000):
        build_area = 1000

    state_msa = getMSANameForCounty(county, state)

    if(state_msa==False):
        return False

    stateCountyMapping = getStateCountyMapping(state,state_msa)
    stateCountyMeanEncoding = getMeanEncodingForStateCounty(stateCountyMapping)

    qualityMapping = getQualityMapping(build_quality)
    basementMapping = getBasementMapping(basement_type)
    walltypeMapping = getWallTypeMapping(walltype)
    walltypeMapping_1_hot = getOneHotEncoding(np.array(walltypeMapping),7)

    cost_model = getPredictionModel()

    user_input = [[qualityMapping,story_n,build_area,stateCountyMeanEncoding]]
    user_input = np.append(user_input,walltypeMapping_1_hot)
    user_input = user_input.reshape(1,-1)

    msacc = cost_model.predict(user_input)
    return np.float64(round(msacc[0],2))


def calculateTotalConstructionCost(state,msacc,area,build_quality='BRONZE',basement_type='NO',area_garage=0,area_basement=0,\
                            bathrooms_full_n=1,bathrooms_half_n=1,kitchen_n=1,unfinished_scaling_factor=0.55):

    construction_cost = round(msacc * area)

#     print('Sq Ft Cost:',msacc,',Construction Cost:',construction_cost)

    qualityMapping = getQualityMapping(build_quality)
    basementMapping = getBasementMapping(basement_type)

    unheated_area = 0
    unheated_area += area_garage
    heated_area = area
    addonCostDict = getAddonCost(state,qualityMapping)
    if(bathrooms_full_n>1):
        construction_cost += (bathrooms_full_n-1)*addonCostDict['bath_full']
    if(bathrooms_half_n>1):
        construction_cost += (bathrooms_half_n-1)*addonCostDict['bath_half']
    if(kitchen_n>1):
        construction_cost += (kitchen_n-1)*addonCostDict['kitchen']
    
    construction_cost += area_garage * msacc * unfinished_scaling_factor
    if(basementMapping==1):
        construction_cost += area_basement * msacc * unfinished_scaling_factor
        unheated_area += area_basement
    if(basementMapping==2):
        construction_cost += area_basement * msacc
    
    return construction_cost

def removeOutlierComps(cmp_items_arr):
    non_lot_cmps = removeEmptyLotComps(cmp_items_arr)
    non_lot_cmps_n = len(non_lot_cmps)
    if(non_lot_cmps_n<3):
        return False
    if(non_lot_cmps_n>20):
        non_lot_cmps = non_lot_cmps[0:20]
        true_cmps = removeOutliersBasedonPrice(non_lot_cmps)
        if(len(true_cmps)>10):
            true_cmps = true_cmps[0:11]
        return true_cmps
    true_cmps = removeOutliersBasedonPrice(non_lot_cmps)
    if(len(true_cmps)<3):
        return False
    if(len(true_cmps)>10):
        true_cmps = true_cmps[0:11]
    return true_cmps

def removeOutliersBasedonPrice(cmp_items_arr):
    cmp_items_arr_trimmed = []
    sale_values = [cmp_item.deeds_sale_amount for cmp_item in cmp_items_arr]
    print('sale values : ',sale_values)
    med_sale_val = np.median(sale_values)
    print('Median sales value : ',med_sale_val)
    allowd_diff = 0.7 * med_sale_val
    for idx,cmp_item in enumerate(cmp_items_arr):
        if(abs(cmp_item.deeds_sale_amount - med_sale_val) <= allowd_diff):
            if(len(cmp_items_arr_trimmed)<10):
                cmp_items_arr_trimmed.append(cmp_item)
    return cmp_items_arr_trimmed

def removeEmptyLotComps(cmp_items_arr):
    nonLotComps = [cmp_item for cmp_item in cmp_items_arr if cmp_item.price_per_sq_ft>55]
    return nonLotComps

def getComparablesObjsArray(st_address,city,state):
        attom_comp_resp = callAttomComparableAPI(st_address,city,state)
        if(attom_comp_resp==False):
                return False
        try :
                cmp_objs = attom_comp_resp.get('RESPONSE_GROUP').get('RESPONSE').get('RESPONSE_DATA').get('PROPERTY_INFORMATION_RESPONSE_ext').get('SUBJECT_PROPERTY_ext').get('PROPERTY')
        except Exception as err:
                # return False
                print('No comps data')
                return False
        comps_received_n = len(cmp_objs)
        print('Raw Comps:',comps_received_n)
        if(comps_received_n<3):
                print('No comps data')
                return False
        cmp_items_arr = []
        for i in range(comps_received_n):
                cmp_i = cmp_objs[i]
                try:
                        cmp_price_per_sq_ft = cmp_i.get('COMPARABLE_PROPERTY_ext').get('SALES_HISTORY').get('@PricePerSquareFootAmount')
                        cmp_price_per_sq_ft = 0 if (cmp_price_per_sq_ft is None or cmp_price_per_sq_ft=='')  else float(cmp_price_per_sq_ft)
                except Exception as err:
                        cmp_price_per_sq_ft = 0

                try:
                        cmp_deeds_sale_amount = cmp_i.get('COMPARABLE_PROPERTY_ext').get('SALES_HISTORY').get('@PropertySalesAmount')
                        cmp_deeds_sale_amount = 0 if (cmp_deeds_sale_amount is None or cmp_deeds_sale_amount=='') else float(cmp_deeds_sale_amount)
                except Exception as err:
                        cmp_deeds_sale_amount = 0

                try:
                        cmp_area = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('@GrossLivingAreaSquareFeetCount')
                        cmp_area = 0 if (cmp_area is None or cmp_area=='') else float(cmp_area)
                except Exception as err:
                        cmp_area = 0

                try:
                        cmp_lot_size = cmp_i.get('COMPARABLE_PROPERTY_ext').get('SITE').get('@LotSquareFeetCount')
                        cmp_lot_size = 0 if (cmp_lot_size is None or cmp_lot_size =='') else float(cmp_lot_size)
                except Exception as err:
                        cmp_lot_size = 0

                try:
                        cmp_bedroom_count = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('@TotalBedroomCount')
                        cmp_bedroom_count = 0 if (cmp_bedroom_count is None or cmp_bedroom_count =='') else int(cmp_bedroom_count)
                except Exception as err:
                        cmp_bedroom_count = 0

                try:
                        cmp_baths_total = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('@TotalBathroomCount')
                        cmp_baths_total = 0 if (cmp_baths_total is None or cmp_baths_total =='') else float(cmp_bedroom_count)
                except Exception as err:
                        cmp_baths_total = 0

                try:
                        cmp_baths_half = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('@TotalBathroomHalfCount_ext')
                        cmp_baths_half = 0 if (cmp_baths_half is None or cmp_baths_half =='') else int(cmp_baths_half)
                except Exception as err:
                        cmp_baths_half = 0

                try:
                        cmp_baths_full = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('@TotalBathroomFullCount_ext')
                        cmp_baths_full = 0 if (cmp_baths_full is None or cmp_baths_full =='') else int(cmp_baths_full)
                except Exception as err:
                        cmp_baths_full = 0

                try:
                        story_count = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('@StoriesCount')
                        story_count = 0 if (story_count is None or story_count =='') else int(story_count)
                except Exception as err:
                        story_count = 0

                try:
                        cmp_year_build = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('STRUCTURE_ANALYSIS').get('@PropertyStructureBuiltYear')
                        cmp_year_build = 0 if (cmp_year_build is None or cmp_year_build =='') else int(cmp_year_build)
                except Exception as err:
                        cmp_year_build = 0

                try:
                        cmp_distance = cmp_i.get('COMPARABLE_PROPERTY_ext').get('@DistanceFromSubjectPropertyMilesCount')
                        cmp_distance = 0 if (cmp_distance is None or cmp_distance =='') else float(cmp_distance)
                except Exception as err:
                        cmp_distance = 0
                
                try:
                        cmp_garage_area = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('CAR_STORAGE').get('CAR_STORAGE_LOCATION').get('@SquareFeetCount')
                        cmp_garage_area = 0 if (cmp_garage_area is None or cmp_garage_area =='') else float(cmp_garage_area)
                except Exception as err:
                        cmp_garage_area = 0
                
                try:
                        cmp_basement_total_area = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('BASEMENT').get('@SquareFeetCount')
                        cmp_basement_total_area = 0 if (cmp_basement_total_area is None or cmp_basement_total_area =='') else float(cmp_basement_total_area)
                except Exception as err:
                        cmp_basement_total_area = 0

                try:
                        cmp_basement_finish_percent = cmp_i.get('COMPARABLE_PROPERTY_ext').get('STRUCTURE').get('BASEMENT').get('@_FinishedPercent')
                        cmp_basement_finish_percent = 0 if (cmp_basement_finish_percent is None or cmp_basement_finish_percent =='') else float(cmp_basement_finish_percent)
                except Exception as err:
                        cmp_basement_finish_percent = 0
                cmp_basement_finished_area = 0
                cmp_basement_unfinished_area = 0

                if(cmp_basement_finish_percent>=0):
                        cmp_basement_finished_area = cmp_basement_total_area*cmp_basement_finish_percent
                        
                cmp_basement_unfinished_area = cmp_basement_total_area - cmp_basement_finished_area

                try:
                        cmp_address = cmp_i.get('COMPARABLE_PROPERTY_ext').get('@_StreetAddress')+','+\
                                        cmp_i.get('COMPARABLE_PROPERTY_ext').get('@_City')+','+cmp_i.get('COMPARABLE_PROPERTY_ext').get('@_State')
                except Exception as err:
                        cmp_address = ''
                if(cmp_price_per_sq_ft==0):
                        if(cmp_deeds_sale_amount!=0 and cmp_area!=0):
                                cmp_price_per_sq_ft = cmp_deeds_sale_amount/cmp_area
                                
                if(cmp_deeds_sale_amount!=0 and cmp_area!=0 and cmp_year_build!=0):
                        cmp_items_arr.append(Comparable(cmp_address,cmp_distance,cmp_area,cmp_bedroom_count,\
                                                        cmp_baths_full,cmp_baths_half,story_count,cmp_year_build,\
                                                        cmp_lot_size,cmp_garage_area,cmp_basement_total_area,cmp_basement_finished_area,\
                                                        cmp_basement_unfinished_area,cmp_price_per_sq_ft,cmp_deeds_sale_amount))
        print('Final comps:',len(cmp_items_arr))
        if(len(cmp_items_arr)<3):
            return False
        cmp_items_arr = removeOutlierComps(cmp_items_arr)
        return cmp_items_arr

def adjustmentYear(diff_year,cmp_price):
    adj_year = 0
    print('diff year:',diff_year,'type(diff_year):',type(diff_year))
    if(abs(diff_year)>=71):
        adj_year = cmp_price*.15
    elif(abs(diff_year)>=41 & abs(diff_year)<=70):
        adj_year = cmp_price*.1
    elif(abs(diff_year)>=21 & abs(diff_year)<=40):
        adj_year = cmp_price*.05
    else:
        adj_year = 0
    if(diff_year<0):
        cmp_price += adj_year
    else:
        cmp_price -= adj_year
    return cmp_price


def adjustmentCoveredArea(diff_area,cmp_price,cmp_price_per_sq_ft):
    adj_area = 0
    adj_area = abs(diff_area) * cmp_price_per_sq_ft
    if(diff_area<0):
        cmp_price += adj_area
    else:
        cmp_price -= adj_area
    return cmp_price


def adjustmentBathHalf(diff_bath_half,diff_year,cmp_price):
    half_bath_base_price = 4000
    alpha_bh = 200
    
    if(diff_bath_half==0):
        if(diff_year<0):
            cmp_price +=  (abs(diff_year/10)*alpha_bh)
        else:
            cmp_price -=  (abs(diff_year/10)*alpha_bh)
    
    if(diff_bath_half!=0):
        if((diff_year<0) & (diff_bath_half<0)):
            cmp_price = cmp_price + abs(diff_bath_half)*half_bath_base_price + (abs(diff_year/10)*alpha_bh)
        if((diff_year<0) & (diff_bath_half>0)):
            cmp_price = cmp_price - (abs(diff_bath_half)*half_bath_base_price - (abs(diff_year/10)*alpha_bh))
        if((diff_year>0) & (diff_bath_half<0)):
            cmp_price = cmp_price + abs(diff_bath_half)*half_bath_base_price - (abs(diff_year/10)*alpha_bh)
        if((diff_year>0) & (diff_bath_half>0)):
            cmp_price = cmp_price - abs(diff_bath_half)*half_bath_base_price - (abs(diff_year/10)*alpha_bh)

    return cmp_price

def adjustmentBathFull(diff_bath_full,diff_year,cmp_price):
    full_bath_base_price = 8000
    alpha_bf = 400
    
    if(diff_bath_full==0):
        if(diff_year<0):
            cmp_price += (abs(diff_year/10)*alpha_bf)
        else:
            cmp_price -= (abs(diff_year/10)*alpha_bf)
    
    if(diff_bath_full!=0):
        if((diff_year<0) & (diff_bath_full<0)):
            cmp_price = cmp_price + abs(diff_bath_full)*full_bath_base_price + (abs(diff_year/10)*alpha_bf)
        if((diff_year<0) & (diff_bath_full>0)):
            cmp_price = cmp_price - (abs(diff_bath_full)*full_bath_base_price - (abs(diff_year/10)*alpha_bf))
        if((diff_year>0) & (diff_bath_full<0)):
            cmp_price = cmp_price + abs(diff_bath_full)*full_bath_base_price - (abs(diff_year/10)*alpha_bf)
        if((diff_year>0) & (diff_bath_full>0)):
            cmp_price = cmp_price - abs(diff_bath_full)*full_bath_base_price - (abs(diff_year/10)*alpha_bf)

    return cmp_price

def adjustmentGarageArea(diff_garage_area,cmp_price,cmp_price_per_sq_ft):
    adj_garage_area = 0
    adj_garage_area = abs(diff_garage_area) * cmp_price_per_sq_ft * 0.55
    if(diff_garage_area<0):
        cmp_price += adj_garage_area
    else:
        cmp_price -= adj_garage_area
    return cmp_price

def adjustmentBasementArea(diff_basement_area_finished,diff_basement_area_unfinished,cmp_price,cmp_price_per_sq_ft):
    adj_basement_area_finished = 0
    adj_basement_area_finished = abs(diff_basement_area_finished) * cmp_price_per_sq_ft
    if(diff_basement_area_finished<0):
        cmp_price += adj_basement_area_finished
    else:
        cmp_price -= adj_basement_area_finished

    adj_basement_area_unfinished = 0
    adj_basement_area_unfinished = abs(diff_basement_area_unfinished) * cmp_price_per_sq_ft * 0.55
    if(diff_basement_area_unfinished<0):
        cmp_price += adj_basement_area_unfinished
    else:
        cmp_price -= adj_basement_area_unfinished

    return cmp_price


def adjustComparablePrice(query_property,comparable_property):
    q_year_build = query_property.year
    q_area = query_property.area
    q_baths_full = query_property.full_bath_n
    q_baths_half = query_property.half_bath_n
    q_bedrooms = query_property.bed_n
    q_garage_area = query_property.garage_area
    q_basement_area_finished = query_property.basement_area_finished
    q_basement_area_unfinished = query_property.basement_area_unfinished

    adj_price = comparable_property.deeds_sale_amount
    cmp_year_build = comparable_property.year
    cmp_area = comparable_property.area
    cmp_price_per_sq_ft = comparable_property.price_per_sq_ft
    cmp_baths_full = comparable_property.full_bath_n
    cmp_baths_half =  comparable_property.half_bath_n
    cmp_lot_size = comparable_property.lot_area
    cmp_bedroom_count = comparable_property.bed_n
    cmp_garage_area = comparable_property.garage_area
    cmp_basement_area_finished = comparable_property.basement_area_finished
    cmp_basement_area_unfinished = comparable_property.basement_area_unfinished

    diff_year = int(cmp_year_build - q_year_build)
    diff_area = int(cmp_area - q_area)
    diff_bath_full = int(cmp_baths_full - q_baths_full)
    diff_bath_half = int(cmp_baths_half - q_baths_half)
    diff_garage_area = int(cmp_garage_area - q_garage_area)
    diff_basement_area_finished = int(cmp_basement_area_finished - q_basement_area_finished)
    diff_basement_area_unfinished = int(cmp_basement_area_unfinished - q_basement_area_unfinished)
    adj_price = adjustmentYear(diff_year,adj_price)
    adj_price = adjustmentCoveredArea(diff_area,adj_price,cmp_price_per_sq_ft)
    adj_price = adjustmentBathHalf(diff_bath_half,diff_year,adj_price)
    adj_price = adjustmentBathFull(diff_bath_full,diff_year,adj_price)
    adj_price = adjustmentGarageArea(diff_garage_area,adj_price,cmp_price_per_sq_ft)
    # adj_price = adjustmentBasementArea(diff_basement_area_finished,diff_basement_area_unfinished,adj_price,cmp_price_per_sq_ft)

    return adj_price


def setAndGetAdjustedValuesofComparables(cmp_items_arr,query_prop):
    comparables_adjst_prices = [adjustComparablePrice(query_prop,cmp_item) for cmp_item in cmp_items_arr]
    for idx,cmp_item in enumerate(cmp_items_arr):
        cmp_item.setZillowLink()
        cmp_item.setValue(comparables_adjst_prices[idx])
        # cmp_item.print()
    return comparables_adjst_prices

def getVACofQueryPropertyObj(cmp_items_arr,comparables_adjst_prices):
    sorted_comps_idx=np.argsort(comparables_adjst_prices)
    cmps_arr_n = len(sorted_comps_idx)
    mid_idx = int(np.floor(cmps_arr_n/2))
    mid_comps_adjst_prices = cmp_items_arr[sorted_comps_idx[mid_idx]].value
    q_vac = int(np.mean(comparables_adjst_prices))
    q_vac2 = int(np.mean(mid_comps_adjst_prices))
    return q_vac,q_vac2

def getKPI(archi_plan,street_address,city='TULSA',state='OK',build_quality='BRONZE',basement_type='NO',\
           land_value=0,walltype='Brick Veneer - Wood Frame'):
    
    msacc = predictConstructionCostFromModel(state,city, archi_plan.area_total,build_quality,\
                                             story_n=archi_plan.story_n,walltype=walltype)
    
    construction_cost = calculateTotalConstructionCost(state,msacc,archi_plan.area_total,build_quality,basement_type,\
                                                       area_garage=archi_plan.area_garage,\
                                                       area_basement = archi_plan.area_basement,\
                                                       bathrooms_full_n=archi_plan.bathrooms_full_n,\
                                                       bathrooms_half_n=archi_plan.bathrooms_half_n)
    
    query_prop_for_comp = Comparable('',0,archi_plan.area_total,archi_plan.bedrooms_n,archi_plan.bathrooms_full_n,\
                               archi_plan.bathrooms_half_n,archi_plan.story_n,2024,5000,archi_plan.area_garage,archi_plan.area_basement,\
                                0,archi_plan.area_basement,0,0)
    
    validated_address = validateAddress(street_address+','+city+','+state)
    parcel_lat, parcel_lng = validated_address['lat'],validated_address['lng']

    cmp_items_arr=getComparablesObjsArrayFromZillow(street_address,city,state,query_prop_for_comp,parcel_lat, parcel_lng)
    if(cmp_items_arr==False):
        kpi_val = KPI(0,0,construction_cost, land_value, msacc)
        return kpi_val
    comparables_adjst_prices = setAndGetAdjustedValuesofComparables(cmp_items_arr,query_prop_for_comp)
    vac_min,vac_max = getVACofQueryPropertyObj(cmp_items_arr,comparables_adjst_prices)
    kpi_val = KPI(vac_min,vac_max,construction_cost,land_value,msacc)
    kpi_val.setVACbasedonQuality(vac_min,vac_max,build_quality)
    return kpi_val


def callAttomComparableAPI(st_address,city,state,lot_area=45000):
    comp_address_uri_encoded = urllib.parse.quote(st_address)
    attom_comp_url = 'https://api.gateway.attomdata.com/property/v2/salescomparables/address/'+comp_address_uri_encoded+'/'+city+'/US/'+state+'/-?searchType=Radius&minComps=1&maxComps=20&miles=2&useSameTargetCode=false&useCode=RSFR&sameCity=true&bedroomsRange=5&bathroomRange=5&sqFeetRange=5000&lotSizeRange='+str(lot_area)+'&saleDateRange=12&yearBuiltRange=10&include0SalesAmounts=false&ownerOccupied=Both&distressed=IncludeDistressed'
    headers = {'apikey': settings.ATTOM_API_KEY,'accept': "application/json", }
    attom_comp_resp = requests.get(attom_comp_url,headers=headers)
    if attom_comp_resp.status_code!=200:
        return False
    compAPIresp = False
    try :
        compAPIresp = attom_comp_resp.json()  
    except Exception as err:
        compAPIresp = False
    return compAPIresp


def getShortListedPlans(p_width,p_depth,max_buildable_area,min_buildable_area):
    plans_data = pd.read_csv('./ml_models/data/architectural_plans/architectural_plans_preprocessed.csv')

    shortlisted_plans = plans_data.loc[(plans_data['width'] <= p_width) & (plans_data['depth'] <= p_depth) &\
                                        (plans_data['area_total'] >= min_buildable_area) & (plans_data['area_total'] <=max_buildable_area)]
    shortlisted_plans_n = len(shortlisted_plans)

    shortlisted_plans_arr = []

    for idx in range(shortlisted_plans_n):
        plan = shortlisted_plans.iloc[idx]
        shortlisted_plans_arr.append(ArchitecturalPlan(plan[0],plan[1],plan[2],plan[3],\
                                                        plan[4],plan[5],plan[6],plan[7],\
                                                        plan[8],plan[9],plan[10],plan[11],\
                                                        plan[12],plan[13],plan[14],plan[15],\
                                                        plan[16],plan[17],plan[18],plan[19],\
                                                        plan[20],plan[21],plan[22],plan[23],plan[24]))
    
    return shortlisted_plans_arr


def maximizeROI(st_address,city,county,state,width,depth,height,max_buildable_area,land_acquisition_cost):
    comps = getComparablesObjsArray(st_address,city,state)
    comp_areas = [cmp_i.area for cmp_i in comps ] 
    max_comp_area = max(comp_areas)
    min_comp_area = min(comp_areas)

    max_opt_area = min(max_comp_area*1.15,max_buildable_area)

    print('Max comp area:',max_comp_area,' Max Buildable area:',\
          max_buildable_area,' Max Opt Area:',max_opt_area, 'Min comp area:',min_comp_area)

    plans_arr = getShortListedPlans(width,depth,max_opt_area,max_comp_area)
    shortlisted_plans_n = len(plans_arr)
    print('Plans count:',shortlisted_plans_n)
    model_input_p1 = np.array([[plan.story_n,plan.area_total] for plan in plans_arr])
    model_input = np.concatenate((model_input_p1, model_input_p1,model_input_p1))

    qual_arr = np.repeat([0,1,2], shortlisted_plans_n)
    qual_arr = qual_arr.reshape(shortlisted_plans_n*3,1)

    model_input = np.hstack((qual_arr, model_input))

    print('County:',county)
    state_msa = getMSANameForCounty(county, state)
    print('State_msa:',state_msa)

    if(state_msa==False):
        return False

    stateCountyMapping = getStateCountyMapping(state,state_msa)
    stateCountyMeanEncoding = getMeanEncodingForStateCounty(stateCountyMapping)
    wallTypeMapping = getWallTypeMapping('Brick Veneer - Wood Frame')

    mean_arr = np.ones((shortlisted_plans_n*3,1))*stateCountyMeanEncoding
    wallType_arr = np.ones(shortlisted_plans_n*3)*wallTypeMapping
    wallType_arr = wallType_arr.astype(int)
    wallType_1hot = getOneHotEncoding(wallType_arr,7)

    model_input = np.hstack((model_input, mean_arr))
    model_input = np.hstack((model_input, wallType_1hot))

    cost_model = getPredictionModel()

    msaccs = cost_model.predict(model_input)

    info_mat = pd.DataFrame(columns=['plan_name', 'area', 'story','quality','construction_cost','total_cost','vac','equity'])
    plan_number_arr = [plan.plan_number for plan in plans_arr]
    info_mat['plan_name'] =  np.concatenate((plan_number_arr, plan_number_arr,plan_number_arr))
    info_mat['area'] = model_input[:,2]
    info_mat['story'] = model_input[:,1]
    info_mat['quality'] = model_input[:,0]

    construction_cost_arr = np.ones((shortlisted_plans_n*3,1))
    total_cost_arr = np.ones((shortlisted_plans_n*3,1))
    vac_arr = np.ones((shortlisted_plans_n*3,1))
    equity_arr = np.ones((shortlisted_plans_n*3,1))

    quality_arr = ['BRONZE','SILVER','GOLD']

    for idx,plan in enumerate(plans_arr):
        query_prop_for_comp = Comparable('',0,plan.area_total,plan.bedrooms_n,plan.bathrooms_full_n,\
                               plan.bathrooms_half_n,plan.story_n,2024,5000,plan.area_garage,plan.area_basement,\
                                0,plan.area_basement,0,0)

        comparables_adjst_prices = setAndGetAdjustedValuesofComparables(comps,query_prop_for_comp)
        vac_min,vac_max = getVACofQueryPropertyObj(comps,comparables_adjst_prices)

        for idx1,quality_val in enumerate(quality_arr):
            # msacc = predictPerSqFtCost(state,city, plan.area_total,quality_val,plan.story_n)
            msacc = msaccs[idx+(shortlisted_plans_n*idx1)]
            construction_cost = calculateTotalConstructionCost(state,msacc,plan.area_total,area_garage=plan.area_garage,area_basement=0,\
                            bathrooms_full_n = plan.bathrooms_full_n,bathrooms_half_n=plan.bathrooms_half_n)

            kpi_val = KPI(vac_min,vac_max,construction_cost,land_acquisition_cost,msacc)
            kpi_val.setVACbasedonQuality(vac_min,vac_max,quality_val)

            construction_cost_arr[idx+(shortlisted_plans_n*idx1)] = construction_cost
            total_cost_arr[idx+(shortlisted_plans_n*idx1)] = kpi_val.total_project_cost
            vac_arr[idx+(shortlisted_plans_n*idx1)] = kpi_val.vac_min
            equity_arr[idx+(shortlisted_plans_n*idx1)] = kpi_val.equity_min

        if(idx%25==0):
            print(idx, end =",") 
    
    info_mat['construction_cost'] =  construction_cost_arr
    info_mat['total_cost'] = total_cost_arr
    info_mat['vac'] = vac_arr
    info_mat['equity'] = equity_arr

    max_roi_plan = np.array(info_mat.loc[info_mat['equity'] == max(info_mat['equity'])])
    max_roi_info = {}
    max_roi_info['plan_number'] = max_roi_plan[0][0]
    max_roi_info['quality'] = quality_arr[int(max_roi_plan[0][3])]
    max_roi_info['construction_cost'] = max_roi_plan[0][4]
    max_roi_info['vac'] = max_roi_plan[0][6]
    max_roi_info['equity'] = max_roi_plan[0][7]

    return max_roi_info


def callAttomPropertyAPI(addrs_part1,addrs_part2):
    addrs_part1_uri = urllib.parse.quote(addrs_part1)
    addrs_part2_uri = urllib.parse.quote(addrs_part2)
    attom_url = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/expandedprofile?address1='+addrs_part1_uri+'&address2='+addrs_part2_uri+'&debug=True'
    headers = {'apikey': settings.ATTOM_API_KEY,'accept': "application/json", }
    attom_resp = requests.get(attom_url,headers=headers)
    return attom_resp.json()

def getPopulatedParcelFromAttom(address_p1, address_p2):
    attom_resp_json = callAttomPropertyAPI(address_p1,address_p2)
    if(attom_resp_json==False):
        return False

    p_cord = []
    
    try :
            cmn_path = attom_resp_json.get('property')[0]
    except Exception as err:
            print('No Property data')
            return False

    try :
            p_attom_id = cmn_path.get('identifier').get('attomId')
    except Exception as err:
            p_attom_id = 0
    
    try :
            p_lat = cmn_path.get('location').get('latitude')
            p_lat = float(p_lat) if (p_lat is not None) else 0.0   
    except Exception as err:
            p_lat = 0

    try :
            p_lng = cmn_path.get('location').get('longitude')
            p_lng = float(p_lng) if (p_lng is not None) else 0.0   
    except Exception as err:
            p_lng = 0
        
    try :
            p_area = cmn_path.get('lot').get('lotSize2')
            p_area = float(p_area) if (p_area is not None) else 0.0   
    except Exception as err:
            p_area = 0

    try :
            p_tax_amount = cmn_path.get('assessment').get('tax').get('taxAmt')
            p_tax_amount = float(p_tax_amount) if (p_tax_amount is not None) else 0.0   
    except Exception as err:
            p_tax_amount = 0

    try :
            p_owner_name = cmn_path.get('assessment').get('owner').get('owner1').get('fullName')
            p_owner_name = p_owner_name if (p_owner_name is not None) else ''   
    except Exception as err:
            p_owner_name = ''

    try :
            p_zoning_classification = cmn_path.get('lot').get('siteZoningIdent')
            p_zoning_classification = p_zoning_classification if (p_zoning_classification is not None) else ''   
    except Exception as err:
            p_zoning_classification = ''

    try :
            p_zoning_dscrp = cmn_path.get('summary').get('propClass')
            p_zoning_dscrp = p_zoning_dscrp if (p_zoning_dscrp is not None) else ''   
    except Exception as err:
            p_zoning_dscrp = ''

    try :
            p_type = cmn_path.get('lot').get('zoningType')
            p_type = p_type if (p_type is not None) else ''   
    except Exception as err:
            p_type = ''

    try :
            p_county = cmn_path.get('area').get('munName')
            p_county = p_county if (p_county is not None) else ''   
    except Exception as err:
            p_county = ''

    try :
            p_state = cmn_path.get('address').get('countrySubd')
            p_state = p_state if (p_state is not None) else ''   
    except Exception as err:
            p_state = ''

    try :
            p_city = cmn_path.get('address').get('locality')
            p_city = p_city if (p_city is not None) else ''   
    except Exception as err:
            p_city = ''

    try :
            p_street_adr = cmn_path.get('address').get('line1')
            p_street_adr = p_street_adr if (p_street_adr is not None) else ''   
    except Exception as err:
            p_street_adr = ''

    try :
            p_parcel_id = cmn_path.get('identifier').get('apn')
            p_parcel_id = p_parcel_id if (p_parcel_id is not None) else ''   
    except Exception as err:
            p_parcel_id = ''

    try :
            p_query_address = cmn_path.get('address').get('oneLine')
            p_query_address = p_query_address if (p_query_address is not None) else ''   
    except Exception as err:
            p_query_address = ''

    try :
            p_land_value = cmn_path.get('assessment').get('market').get('mktLandValue')
            p_land_value = float(p_land_value) if (p_land_value is not None) else 25000   
    except Exception as err:
            p_land_value = 25000

    propertyObj = Property(p_attom_id,p_cord,p_lat,p_lng,p_area,'',p_tax_amount,\
                p_city,p_state,p_county,p_street_adr,p_query_address,p_parcel_id,\
                p_type,p_zoning_classification,p_zoning_dscrp,p_owner_name,p_land_value)

    return propertyObj

def getSchoolDistrictFromAttom(attom_id):
    school_district = ''
#     attom_school_district_api_endpoint = 'https://api.gateway.attomdata.com/propertyapi/v4/property/detailwithschools?attomid='+attom_id
#     headers = {'apikey': ATTOM_API_KEY,'accept': "application/json", }
#     attom_resp = requests.get(attom_school_district_api_endpoint,headers=headers)
#     if attom_comp_resp.status_code!=200:
        # return school_district
#     try:
#             school_district = attom_resp.json().get('property')[0].get('schoolDistrict')('districtname')
#     except Exception as err:
#             school_district = school_district
    return school_district

def getPropertyInfo(full_address, street_address, city, state):
    attom_data, created = AttomData.objects.get_or_create(address=full_address)

    if not created and attom_data.property:
        property_data = attom_data.property
    else:
        street_address = street_address
        city_state = f"{city}, {state}"
        property = getPopulatedParcelFromAttom(street_address, city_state)
        if not property:
            return None
        property_data = {
            'land_acquisition_cost': property.land_cost,
            'parcel_id': property.parcel_id,
            'property_type': property.zoning_dscrp
        }

        attom_data.property = property_data
        attom_data.save()
    return property_data


def compute_length(point1,point2):
    '''
    Function returns the distance (miles) between two (lat,lng) coordinates 

    Parameters
    ----------
    point1 : [lat,lng] point as double
    point1 : [lat,lng] point as double

    Returns
    -------
    dist : double
        distance in miles.
    '''
    point1_rad = [radians(_) for _ in point1]
    point2_rad = [radians(_) for _ in point2]
    dist = haversine_distances([point1_rad, point2_rad])
    dist = dist * 6371000/1000 * 3280.84  # multiply by Earth radius to get kilometers
    return round(dist[0][1]/5280,1)


def getCompsWithinNMiles(comps_arr,parcel_coords,dist_N=3):
    '''
    Function returns the list of 20 comparables that are within N(default 2) miles 
    from the query property 

    Parameters
    ----------
    comps_arr : an array of comparables
    parcel_coords : an array representing [lat,lng] latitude and longitide of query address
    dist_N : double 

    Returns
    -------
    comps_arr_in_n_miles_kNN : dataframe
        20 comparables within N miles.
    '''
    comps_in_n_miles_idx = [index for index, row in comps_arr.iterrows() if compute_length(parcel_coords,[row['lat'],row['lng']])<dist_N]
    comps_in_n_miles = comps_arr.iloc[comps_in_n_miles_idx]
    comps_in_n_miles_dist = np.zeros(len(comps_in_n_miles))
    i=0
    for index,cmp_item in comps_in_n_miles.iterrows():
          comp_i_dist = compute_length(parcel_coords,[cmp_item['lat'],cmp_item['lng']])
          if(comp_i_dist==0):
                comps_in_n_miles_dist[i] = 100
          else:
                comps_in_n_miles_dist[i] = comp_i_dist
          i+=1
    K = 20
    smallest_indices = heapq.nsmallest(
        K, range(len(np.array(comps_in_n_miles_dist))), key=np.array(comps_in_n_miles_dist).__getitem__)
    
    comps_arr_in_n_miles = comps_in_n_miles.iloc[smallest_indices]
    return comps_arr_in_n_miles

def normalizeComps(comps_data,query_parcel):
    '''
    Function normalizes the dataframe of comparables w.r.t. the query parcel data 

    Parameters
    ----------
    comps_data : array of comparables
    query_parcel : comparable object 

    Returns
    -------
    comps_normalized : dataframe
        normalized comparables w.r.t. the query parcel data.
    '''

    comps_normalized = pd.DataFrame()

    # comps_max_area = round(query_parcel.area*1.2)
    # comps_min_area = round(query_parcel.area*0.8)
    # comps_normalized = comps_data.loc[(comps_data['covered_area'] >= comps_min_area) \
    #                                         & (comps_data['covered_area'] <= comps_max_area)]
    

    # comps_normalized['bed_count'] = comps_data['bed_count']
    # comps_normalized['bath_full_count'] = comps_data['bath_full_count']
    # comps_normalized['bath_half_count'] = comps_data['bath_half_count']
    # comps_normalized['covered_area'] = comps_data['covered_area']
    
    comps_normalized['bed_count'] = abs(1-comps_data['bed_count']/query_parcel.bed_n)
    comps_normalized['bath_full_count'] = abs(1-comps_data['bath_full_count']/query_parcel.full_bath_n)
    comps_normalized['bath_half_count'] = abs(1-comps_data['bath_half_count']/query_parcel.half_bath_n)
    comps_normalized['covered_area'] = abs(1-comps_data['covered_area']/query_parcel.area)
    comps_normalized['lot_area'] = abs(1-comps_data['lot_area']/query_parcel.lot_area)
    return comps_normalized

def findKNearestComps(comp_arr_normalized,comps_data):
    '''
    Function returns the list of (at max) 10 most similar comparables from the array of 
    normalized comparables 

    Parameters
    ----------
    comp_arr_normalized : an array of normalized comparables
    comps_data : array of comparables 

    Returns
    -------
    comps_arr : dataframe
        (at max) 10 most similar comparables.
    '''

    w= [0.1, 0.15, 0.05, 0.7]
    comps_dist_arr = comp_arr_normalized[['bed_count','bath_full_count','bath_half_count','covered_area']].dot(w)
    K = 10
    smallest_indices = heapq.nsmallest(
        K, range(len(np.array(comps_dist_arr))), key=np.array(comps_dist_arr).__getitem__)
    sorted_idx = comp_arr_normalized.index[smallest_indices]
    comps_arr = comps_data.loc[sorted_idx]

    return comps_arr

def readZillowCompsData():
    '''
    Function reads and loads the zillow comparables data 

    Parameters
    ----------
    

    Returns
    -------
    comps_data : dataframe
        complete comparables informaiton as dataframe.
    '''

    comps_data_raw = pd.read_csv('./ml_models/data/zillow_comparables/tulsa_comps_6_months.csv')
    comps_data = pd.DataFrame()
    comps_data['address'] = comps_data_raw['full_address']
    comps_data['bed_count'] = comps_data_raw['bedrooms']
    comps_data['bath_full_count'] = [math.floor(bath_count) for bath_count in comps_data_raw['full_bathroom']]
    comps_data['bath_half_count'] = comps_data_raw['half_bathroom']
    comps_data['covered_area'] = comps_data_raw['squarefeetarea']
    comps_data['lot_area'] = comps_data_raw['lot_area']
    comps_data['price'] = comps_data_raw['price']
    comps_data['lat'] = comps_data_raw['latitude']
    comps_data['lng'] = comps_data_raw['longitude']
    comps_data['year_built'] = comps_data_raw['year_built']
    comps_data['story_count'] = comps_data_raw['stories']
    comps_data.fillna(0)

    return comps_data




# def compute_length(point1,point2):
#     point1_rad = [radians(_) for _ in point1]
#     point2_rad = [radians(_) for _ in point2]
#     dist = haversine_distances([point1_rad, point2_rad])
#     dist = dist * 6371000/1000 * 3280.84  # multiply by Earth radius to get kilometers
#     return round(dist[0][1]/5280,1)


# def getCompsWithinNMiles(comps_arr,parcel_coords,dist_N=2):
#     comps_in_n_miles_idx = [index for index, row in comps_arr.iterrows() if compute_length(parcel_coords,[row['lat'],row['lng']])<dist_N]
#     comps_in_n_miles = comps_arr.iloc[comps_in_n_miles_idx]
#     comps_in_n_miles_dist = np.zeros(len(comps_in_n_miles))
#     i=0
#     for index,cmp_item in comps_in_n_miles.iterrows():
#           comp_i_dist = compute_length(parcel_coords,[cmp_item['lat'],cmp_item['lng']])
#           if(comp_i_dist==0):
#                 comps_in_n_miles_dist[i] = 100
#           else:
#                 comps_in_n_miles_dist[i] = comp_i_dist
#           i+=1
#     K = 20
#     smallest_indices = heapq.nsmallest(
#         K, range(len(np.array(comps_in_n_miles_dist))), key=np.array(comps_in_n_miles_dist).__getitem__)
    
#     comps_arr_in_n_miles_kNN = comps_in_n_miles.iloc[smallest_indices]
#     return comps_arr_in_n_miles_kNN

# def normalizeComps(comps_data,query_parcel):
#     comps_normalized = pd.DataFrame()
#     # comps_normalized['bed_count'] = abs(1-comps_data['bed_count']/query_parcel.bed_n)
#     # comps_normalized['bath_full_count'] = abs(1-comps_data['bath_full_count']/query_parcel.full_bath_n)
#     # comps_normalized['bath_half_count'] = abs(1-comps_data['bath_half_count']/query_parcel.half_bath_n)
#     # comps_normalized['covered_area'] = abs(1-comps_data['covered_area']/query_parcel.area)
#     # comps_normalized['lot_area'] = abs(1-comps_data['lot_area']/query_parcel.lot_area)
#     comps_normalized['bed_count'] = comps_data['bed_count']
#     comps_normalized['bath_full_count'] = comps_data['bath_full_count']
#     comps_normalized['bath_half_count'] = comps_data['bath_half_count']
#     comps_normalized['covered_area'] = comps_data['covered_area']
#     return comps_normalized

# def findKNearestComps(comp_arr_normalized,comps_data):
#     w= [0.2, 0.15, 0.05, 0.6]
#     comps_dist_arr = comp_arr_normalized.dot(w)
#     # comps_dist_arr = comp_arr_normalized[['bed_count','bath_full_count','bath_half_count','covered_area']].sum(axis='columns')

#     K = 10
#     smallest_indices = heapq.nsmallest(
#         K, range(len(np.array(comps_dist_arr))), key=np.array(comps_dist_arr).__getitem__)
    
#     comps_arr = comps_data.iloc[smallest_indices]
#     return comps_arr

# def readZillowCompsData():
#     comps_data_raw = pd.read_csv('./ml_models/data/zillow_comparables/tulsa_comps.csv')
#     comps_data_raw = comps_data_raw.loc[(comps_data_raw['home_type'] != 'Condominium')]
#     comps_data_raw = comps_data_raw[(comps_data_raw['latitude'].notna()) \
#                                         & (comps_data_raw['longitude'].notna()) \
#                                         & (comps_data_raw['squarefeetarea']!=0) \
#                                         & (comps_data_raw['squarefeetarea'].notna()) \
#                                         & (comps_data_raw['squarefeetarea']>1500) \
#                                         & (comps_data_raw['bedrooms'].notna()) \
#                                         & (comps_data_raw['bathrooms'].notna()) \
#                                         & (comps_data_raw['half_bathroom'].notna()) \
#                                         & (comps_data_raw['lot_area'].notna())]
#     comps_data_raw = comps_data_raw.reset_index()

#     comps_data = pd.DataFrame()
#     comps_data['address'] = [(st_address.replace('"','')+',Tulsa,OK') for st_address in comps_data_raw['street_address']]
#     comps_data['bed_count'] = comps_data_raw['bedrooms']
#     comps_data['bath_full_count'] = [math.floor(bath_count) for bath_count in comps_data_raw['bathrooms'] ]
#     comps_data['bath_half_count'] = comps_data_raw['half_bathroom']
#     comps_data['covered_area'] = comps_data_raw['squarefeetarea']
#     comps_data['lot_area'] = comps_data_raw['lot_area']
#     comps_data['price'] = comps_data_raw['price']
#     comps_data['lat'] = comps_data_raw['latitude']
#     comps_data['lng'] = comps_data_raw['longitude']
#     comps_data.fillna(0)

#     return comps_data

def getComparablesObjsArrayFromZillow(st_address,city,state,query_prop_for_comp,q_parcel_lat,q_parcel_lng):
    comps_data = readZillowCompsData()
    comps_in_n_miles = getCompsWithinNMiles(comps_data,[q_parcel_lat,q_parcel_lng],6)
    comps_normalized = normalizeComps(comps_in_n_miles,query_prop_for_comp)
    comps_arr = findKNearestComps(comps_normalized,comps_in_n_miles)
    comps_received_n = len(comps_arr)
    print('Raw Comps:',comps_received_n)
    if(comps_received_n<3):
            print('No comps data')
            return False
    cmp_items_arr = []
    for index, cmp_item in comps_arr.iterrows():
        cmp_price_per_sq_ft = cmp_item['price']/cmp_item['covered_area']
        cmp_deeds_sale_amount = cmp_item['price']
        cmp_area = cmp_item['covered_area']
        cmp_lot_size = cmp_item['lot_area']
        cmp_bedroom_count = cmp_item['bed_count']
        cmp_baths_full = cmp_item['bath_full_count']
        cmp_baths_half = cmp_item['bath_half_count']
        cmp_baths_total = cmp_baths_half + cmp_baths_full
        story_count = cmp_item['story_count']
        cmp_year_build = cmp_item['year_built']
        cmp_distance = round(compute_length([cmp_item['lat'],cmp_item['lng']],[q_parcel_lat,q_parcel_lng]),2)
        cmp_garage_area = 0
        cmp_basement_total_area = 0
        cmp_basement_finish_percent = 0
        cmp_basement_finished_area = 0
        cmp_basement_unfinished_area = 0

        if(cmp_basement_finish_percent>=0):
                cmp_basement_finished_area = cmp_basement_total_area*cmp_basement_finish_percent
                
        cmp_basement_unfinished_area = cmp_basement_total_area - cmp_basement_finished_area

        cmp_address = cmp_item['address']

        cmp_items_arr.append(Comparable(cmp_address,cmp_distance,cmp_area,cmp_bedroom_count,\
                                        cmp_baths_full,cmp_baths_half,story_count,cmp_year_build,\
                                        cmp_lot_size,cmp_garage_area,cmp_basement_total_area,cmp_basement_finished_area,\
                                        cmp_basement_unfinished_area,cmp_price_per_sq_ft,cmp_deeds_sale_amount))
    print('Final comps:',len(cmp_items_arr))
    if(len(cmp_items_arr)<3):
            return False
    return cmp_items_arr


