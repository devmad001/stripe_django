import pandas as pd, numpy as np

import sys

import glob

import pickle

import json
import requests

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import metrics
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

import os


def getMSANameForCounty(county_name, state_name):
    county_name = county_name.upper().strip()
    state_name = state_name.upper().strip()
    data_path = 'mapping_files/'
    county_to_msa_file =  pd.read_csv(data_path+'county_to_msa_mapping.csv')
    state_county_cmb = state_name+','+county_name
    for msa_name,state_county_val in zip(county_to_msa_file['MSA'],	county_to_msa_file['State_county']):
        if(state_county_cmb == state_county_val):
            return msa_name
    return False
    

def predictConstructionCostFromModel(q_state,q_county,q_quality,q_story_count,q_basement_type,q_area):
    dir_name = 'mapping_files/'
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
    

def calculateTotalConstructionCost(sq_ft_cost, area, area_basement,area_garage, basement_type, unfinished_scaling_factor=0.55):
    total_construction_cost = sq_ft_cost * area + area_garage*sq_ft_cost*unfinished_scaling_factor
    basement_type = basement_type.upper()
    if(basement_type=='FINISHED'):
        total_construction_cost += area_basement*sq_ft_cost
    if(basement_type=='UNFINISHED'):
        total_construction_cost += area_basement*sq_ft_cost*unfinished_scaling_factor
    return int(total_construction_cost)
    
    
q_state = 'al'
q_county = 'decatur'
q_quality = 'bronze'
q_story_count = 2
q_basement_type = 'unfinished'
q_area = 2346
garage_area = 300
basement_area = 400

sq_ft_cost = predictConstructionCostFromModel(q_state,q_county,q_quality,q_story_count,q_basement_type,q_area)
total_construction_cost = calculateTotalConstructionCost(sq_ft_cost, q_area, garage_area,basement_area,'finished')
print('Total Construction Cost : ',total_construction_cost)