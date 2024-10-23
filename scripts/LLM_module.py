import re
import pyap
import urllib.parse
import pickle
import json

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate 
import json


from dotenv import load_dotenv, find_dotenv


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


def extractAddressFromText(txt):
    addresses = pyap.parse(txt, country='US')
    if(len(addresses)<1):
        return False
    for ele in addresses:
        address_str = str(ele)
    return address_str

def verfiyAddress(address_str):
    valid_county_list = ['TULSA','ROGERS','WAGONER','CREEK','OSAGE','WASHINGTON','ATLANTA']
    address_parts = address_str.split(',')
    if(len(address_parts)<3):
        return False
    if(len(address_parts)>4):
        return False
    print('p1')
    st_adr = address_parts[0]
    county = address_parts[1].upper().strip()
    state = address_parts[2].upper().strip()
    print('p2')
    if(len(state)>2):
        state_parts = state.split(' ')
        state = state_parts[0]
        if(state!='OK' or state!='GA'):
            return False
    print(state,county)
    print('p3')
    if(county in valid_county_list and (state=='OK' or state=='GA')):
        return True

def callAttomPropertyAPI(addr_p1,addr_p2):
    addrs_part1_uri = urllib.parse.quote(addr_p1)
    addrs_part2_uri = urllib.parse.quote(addr_p2)
    print('Address Part1 : ',addrs_part1_uri,' Address Part2 : ',addrs_part2_uri)
    # attom_url = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/expandedprofile?address1='+addrs_part1_uri+'&address2='+addrs_part2_uri+'&debug=True'
    # headers = {'apikey': '69f2bfd055eeeff3dd1296afaba9106b','accept': "application/json", }
    # attom_resp = requests.get(attom_url,headers=headers)
    # if(attom_resp.status_code!=200 or len(attom_resp.json()['property'])==0):
    #     return False
    # attom_resp_json = attom_resp.json()
    # return attom_resp_json
    attom_resp_json = {'status': {'version': '1.0.0',
  'code': 0,
  'msg': 'SuccessWithResult',
  'total': 1,
  'page': 1,
  'pagesize': 10,
  'responseDateTime': None,
  'transactionID': '947d5305dcbc65df6a6db61dcb9bf597',
  'attomId': 50697779},
 'echoed_fields': {'jobID': '',
  'loanNumber': '',
  'preparedBy': '',
  'resellerID': '',
  'preparedFor': ''},
 'property': [{'identifier': {'Id': 50697779,
    'fips': '40143',
    'apn': '23575-93-24-13910',
    'multiApn': None,
    'attomId': 50697779},
   'lot': {'depth': None,
    'frontage': None,
    'lotNum': '14',
    'lotSize1': 0.2059917,
    'lotSize2': 8973.0,
    'zoningType': 'Residential',
    'siteZoningIdent': 'RS3',
    'poolType': 'NO POOL'},
   'area': {'blockNum': '16',
    'locType': 'VIEW - NONE',
    'countrySecSubd': 'Tulsa',
    'countyUse1': None,
    'munCode': 'TU',
    'munName': 'TULSA',
    'srvyRange': '13E',
    'srvySection': '24',
    'srvyTownship': '19N',
    'subdName': 'LONGVIEW ACRES 2ND',
    'subdTractNum': None,
    'taxCodeArea': None,
    'censusTractIdent': '8502',
    'censusBlockGroup': '5'},
   'address': {'bldgName': None,
    'country': 'US',
    'countrySubd': 'OK',
    'line1': '8226 E 34TH ST',
    'line2': 'TULSA, OK 74145',
    'locality': 'TULSA',
    'matchCode': 'ExaStr',
    'oneLine': '8226 E 34TH ST, TULSA, OK 74145',
    'postal1': '74145',
    'postal2': '1427',
    'postal3': 'C004',
    'stateFips': '40',
    'unitNumberIdent': None,
    'situsHouseNumber': '8226',
    'situsDirection': 'E',
    'situsStreetName': '34TH',
    'situsAddressSuffix': 'ST',
    'situsPostDirection': None,
    'situsUnitPrefix': None,
    'situsUnitValue': None},
   'location': {'accuracy': 'Rooftop',
    'elevation': None,
    'latitude': '36.112822',
    'longitude': '-95.884130',
    'distance': 0.0,
    'geoid': 'CO40143, CS4093380, DB4030240, ND0000064507, PL4075000, SB0000111339, SB0000111355, SB0000111391, SB0000141256, SB0000143025, SB0000143027, SB0000143028, SB0000144809, SB0000144810, SB0000146622, SB0000148335, SB0000148336, SB0000150137, SB0000150138, SB0000151942, SB0000151943, SB0000153806, ZI74145',
    'geoIdV4': {'CO': '7d2a388acbf1c30054f56f30e1951d11',
     'CS': '29663a66901cea49190d32c263981f34',
     'DB': '762ed132103d9238e1d76c7fa115b081',
     'N2': '5dea386b2f2953ef4c0553d169d26067',
     'PL': 'fa61bed116d6e39d8be1f3cf2bf8b68b',
     'SB': 'ba59b2f402a2a1f9a1205ca71af52619, 606f2309c92120d69663433321e9e241, ba3036ea7d99e7b8451b6c30550bbeb4, 62b87c9020580871394fde49ed2532e0, d026a835260e0d47d36f8810cb108321, b9e94312f27f714df07d9a00b046fbc7, 4206158266a3bea2c7d90860b72f2ec9, 5f491aef768dc7363ebf2eedc8aedb30, ce5a8dfa085fcf9b845f21a17222405c, 0e6c4dbeedadc0f7da071b6c41da48cd, a0ee420251123f10cf379343957e981f, 790c8160a841b25986ec6056da22a0fe, e437d95020a20bb3fe5d81502e7cb1e9, 35c05984cdbbe75b00fbcd5e78306bd7, 89fb4a25715077436b085a5cdcae50d3, 6ef5a9d37d66a9f0424c6d2b3355d5a0, 15aedef4700fa64db5677d3df32dc94a',
     'ZI': 'f9ee4826f2e5503e05a1a504ffc35faf'}},
   'summary': {'archStyle': 'RANCH',
    'absenteeInd': 'OWNER OCCUPIED',
    'propClass': 'Single Family Residence / Townhouse',
    'propSubType': 'Residential',
    'propType': 'SFR',
    'propertyType': 'SINGLE FAMILY RESIDENCE',
    'yearBuilt': 1961,
    'propLandUse': 'SFR',
    'propIndicator': 10,
    'legal1': 'LT 14 BLK 16',
    'descriptionExt': None,
    'codeExt': None,
    'quitClaimFlag': 'False',
    'REOflag': 'False',
    'dateOfLastQuitClaim': None},
   'utilities': {'coolingType': 'CENTRAL',
    'energyType': None,
    'heatingFuel': None,
    'heatingType': 'CENTRAL',
    'sewerType': None},
   'sale': {'sequenceSaleHistory': 1,
    'sellerName': 'AUDREY BELDING',
    'saleSearchDate': '2023-05-23',
    'saleTransDate': '2023-05-17',
    'transactionIdent': '1011416110',
    'amount': {'saleAmt': 216500.0,
     'saleCode': None,
     'saleRecDate': '2023-05-23',
     'saleDisclosureType': 0,
     'saleDocType': None,
     'saleDocNum': '0000040926',
     'saleTransType': 'Resale'},
    'calculation': {'pricePerBed': None, 'pricePerSizeUnit': 112.12}},
   'building': {'size': {'bldgSize': 1931.0,
     'grossSize': 2393.0,
     'grossSizeAdjusted': 1931.0,
     'groundFloorSize': None,
     'livingSize': 1931.0,
     'sizeInd': 'LIVING SQFT',
     'universalSize': 1931.0,
     'atticSize': None},
    'rooms': {'bathFixtures': None,
     'baths1qtr': None,
     'baths3qtr': None,
     'bathsCalc': None,
     'bathsFull': 2,
     'bathsHalf': None,
     'bathsPartial': None,
     'bathsTotal': 2.0,
     'beds': None,
     'roomsTotal': None},
    'interior': {'bsmtSize': 1931,
     'bsmtType': None,
     'bsmtFinishedPercent': 0,
     'floors': None,
     'fplcCount': 1,
     'fplcInd': 'Y',
     'fplcType': 'YES'},
    'construction': {'condition': 'AVERAGE',
     'constructionType': 'FRAME',
     'foundationType': 'SLAB',
     'frameType': 'WOOD',
     'roofCover': 'COMPOSITION SHINGLE',
     'roofShape': None,
     'wallType': 'SIDING',
     'propertyStructureMajorImprovementsYear': None,
     'buildingShapeType': None,
     'buildingShapeDescription': None},
    'parking': {'garageType': 'Garage, Attached',
     'prkgSize': 462.0,
     'prkgSpaces': None,
     'prkgType': 'Garage, Attached'},
    'summary': {'levels': 1,
     'storyDesc': 'MISCELLANEOUS',
     'unitsCount': None,
     'view': 'VIEW - NONE',
     'viewCode': '000'}},
   'assessment': {'appraised': {'apprImprValue': None,
     'apprLandValue': None,
     'apprTtlValue': None},
    'assessed': {'assdImprValue': 12073.0,
     'assdLandValue': 2273.0,
     'assdTtlValue': 14346.0},
    'market': {'mktImprValue': 146080.0,
     'mktLandValue': 27500.0,
     'mktTtlValue': 173580.0},
    'tax': {'taxAmt': 1925.95,
     'taxPerSizeUnit': 1.0,
     'taxYear': 2023.0,
     'exemption': {'ExemptionAmount1': None,
      'ExemptionAmount2': None,
      'ExemptionAmount3': None,
      'ExemptionAmount4': None,
      'ExemptionAmount5': None},
     'exemptiontype': {'Additional': None,
      'Homeowner': None,
      'Disabled': None,
      'Senior': None,
      'Veteran': None,
      'Widow': None}},
    'improvementPercent': 84,
    'owner': {'corporateIndicator': 'N',
     'type': 'INDIVIDUAL',
     'description': 'INDIVIDUAL',
     'ownerAfterSpouse': None,
     'owner1': {'fullName': 'ETHAN W WOOD',
      'lastName': 'WOOD ',
      'firstNameAndMi': 'ETHAN W',
      'trustIndicator': None},
     'owner2': {'fullName': None,
      'lastName': None,
      'firstNameAndMi': None,
      'trustIndicator': None},
     'owner3': {'fullName': 'CHENG WOOD SIXU',
      'lastName': 'SIXU ',
      'firstNameAndMi': 'CHENG WOOD'},
     'owner4': {'fullName': None, 'lastName': None, 'firstNameAndMi': None},
     'absenteeOwnerStatus': 'O',
     'mailingAddressOneLine': '8226 E 34TH ST, TULSA, OK 74145-1427'},
    'mortgage': {'FirstConcurrent': {'trustDeedDocumentNumber': '0000040927',
      'ident': '2023040927',
      'amount': 173000.0,
      'lenderLastName': 'JPMORGAN CHASE BANK NA',
      'companyCode': '16848',
      'date': '2023-05-23',
      'loanTypeCode': 'CNV',
      'deedType': 'WD',
      'term': '361',
      'dueDate': '2053-06-01'},
     'SecondConcurrent': {'amount': 0.0, 'companyCode': '-1'},
     'title': {'companyName': 'OKLAHOMA SECURED TITLE', 'companyCode': None}}},
   'vintage': {'lastModified': '2023-06-02', 'pubDate': '2023-06-02'}}]}
    return attom_resp_json

class Property:
    p_cord = []
    p_lat = 0.0
    p_lng = 0.0
    p_area = 0.0
    p_school_dist = ''
    p_tax_amount = 0
    p_city = ''
    p_state = ''
    p_county = ''
    p_street_adr = ''
    query_address = ''
    p_parcel_id = ''
    p_depth = 0
    p_width=0
    p_depth_after_zoning = 0
    p_width_after_zoning = 0
    p_area_after_zoning = 0
    p_max_area_after_far = 0
    p_type = ''
    p_zoning_classification = ''
    p_zoning_dscrp = ''
    p_owner_name = ''
    
    def __init__(self,p_cord,p_lat,p_lng,p_area,p_school_dist,p_tax_amount,\
                p_city,p_state,p_county,p_street_adr,p_query_address,p_parcel_id,\
                p_type,p_zoning_classification,p_zoning_dscrp,p_owner_name):
        self.p_cord = p_cord
        self.p_lat = p_lat
        self.p_lng = p_lng
        self.p_area = p_area
        self.p_school_dist = p_school_dist
        self.p_tax_amount = p_tax_amount
        self.p_city = p_city
        self.p_state = p_state
        self.p_county = p_county
        self.p_street_adr = p_street_adr
        self.p_query_address = p_query_address
        self.p_parcel_id = p_parcel_id
        self.p_depth = 0
        self.p_width=0
        self.p_depth_after_zoning = 0
        self.p_width_after_zoning = 0
        self.p_area_after_zoning = 0
        self.p_max_area_after_far = 0
        self.p_type = p_type
        self.p_zoning_classification = p_zoning_classification
        self.p_zoning_dscrp = p_zoning_dscrp
        self.p_owner_name = p_owner_name

    def setMaxAreaAfterFar(self,far):
        self.p_max_area_after_far = far*self.p_area


class ZoneInfo:
    zoning_url = ''
    zoning_category = ''
    zoning_classification = ''
    zoning_far = 0.0
    zoning_lot_coverage = 0.0
    zoning_building_height = 0.0
    zoning_min_front_setback = 0.0
    zoning_min_rear_setback = 0.0
    zoning_min_side_setback = 0.0
    zoning_min_lot_size = 0.0
    zoning_min_frontage = 0.0
    zoning_min_depth = 0.0
    zoning_parking_capacity = 0.0
    state = ''
    city = ''
    structure_type=''
    land_use = ''
    def __init__(self,url,category,classification,far,lot_coverage,building_height,\
                 front_setback,rear_setback,side_setback,\
                 lot_size,frontage,depth,parking_capacity,\
                 state ='', city ='', structure_type ='',land_use =''):
        self.zoning_url = url
        self.zoning_category = category
        self.zoning_classification = classification
        self.zoning_far = far
        self.zoning_lot_coverage = lot_coverage
        self.zoning_building_height = building_height
        self.zoning_min_front_setback = front_setback
        self.zoning_min_rear_setback = rear_setback
        self.zoning_min_side_setback = side_setback
        self.zoning_min_lot_size = lot_size
        self.zoning_min_frontage = frontage
        self.zoning_min_depth = depth
        self.zoning_parking_capacity = parking_capacity
        self.state = state
        self.city = city
        self.structure_type= structure_type
        self.land_use= land_use 

def getPropertyObjFromAttomPropertyResponse(attom_resp_json):
    p_cord = []
    p_lat = float(attom_resp_json['property'][0]['location']['latitude']) if ('latitude' in attom_resp_json['property'][0]['location'] and attom_resp_json['property'][0]['location']['latitude'] is not None) else 0.0   
    p_lng = float(attom_resp_json['property'][0]['location']['longitude']) if ('longitude' in attom_resp_json['property'][0]['location'] and attom_resp_json['property'][0]['location']['longitude'] is not None) else 0.0
    p_area = attom_resp_json['property'][0]['lot']['lotSize2'] if ('lotSize2' in attom_resp_json['property'][0]['lot'] and attom_resp_json['property'][0]['lot']['lotSize2'] is not None) else 0.0
    p_tax_amount = attom_resp_json['property'][0]['assessment']['tax']['taxAmt']
    p_owner_name = attom_resp_json['property'][0]['assessment']['owner']['owner1']['fullName']
    p_zoning_classification = attom_resp_json['property'][0]['lot']['siteZoningIdent'] if('siteZoningIdent' in attom_resp_json['property'][0]['lot']['siteZoningIdent'] and attom_resp_json['property'][0]['lot']['siteZoningIdent'] is not None) else ''
    p_zoning_dscrp = attom_resp_json['property'][0]['summary']['propClass']
    p_type = attom_resp_json['property'][0]['lot']['zoningType']
    # p_county = attom_resp_json['property'][0]['area']['munName']
    # p_state = attom_resp_json['property'][0]['address']['countrySubd']
    # p_city = attom_resp_json['property'][0]['address']['locality']
    p_county = 'ATLANTA'
    p_state = 'GA'
    p_city = 'ATLANTA'
    p_street_adr = attom_resp_json['property'][0]['address']['line1']
    p_parcel_id = attom_resp_json['property'][0]['identifier']['apn']
    p_query_address = attom_resp_json['property'][0]['address']['oneLine']
    

    propertyObj = Property(p_cord,p_lat,p_lng,p_area,'',p_tax_amount,\
                p_city,p_state,p_county,p_street_adr,p_query_address,p_parcel_id,\
                p_type,p_zoning_classification,p_zoning_dscrp,p_owner_name)

    return propertyObj


def getZoningInfoFromLLM(state,city,zone_classification):

    zoning_data = None
    if(city.upper()=='ATLANTA'):
        zoning_file = open('zoning_files/atlanta_R4.json')
        zoning_data = json.load(zoning_file)

    if(zoning_data == None):
        return False
    
    z_url = zoning_data[0]['minimum_frontage']['source']
    z_category = 'Single Family Residential'
    z_classification = zoning_data[0]['zoning_code']
    z_far = zoning_data[0]['maximum_floor_area_ratio']['value']
    z_lot_coverage = zoning_data[0]['maximum_lot_coverage']['value']
    z_building_height = 35
    z_front_setback = zoning_data[0]['minimum_front_setback']['value']
    z_rear_setback = zoning_data[0]['minimum_rear_setback']['value']
    z_side_setback = zoning_data[0]['minimum_side_setback']['value']
    z_lot_size = zoning_data[0]['minimum_lot_size']['value']
    z_frontage = zoning_data[0]['minimum_frontage']['value']
    z_depth = 100
    z_parking_capacity = 2
    z_state = zoning_data[0]['minimum_lot_size']['value']
    z_city = zoning_data[0]['minimum_lot_size']['value']
    z_structure_type= 'Duplex'
    z_land_use= 'Land Use'

    zoneObj = ZoneInfo(z_url,z_category,z_classification,z_far,z_lot_coverage,\
                       z_building_height,z_front_setback,z_rear_setback,z_side_setback,\
                       z_lot_size,z_frontage,z_depth,z_parking_capacity,\
                       z_state,z_city,z_structure_type,z_land_use)
    return zoneObj

def getMaxConstructableArea(propertyObj):
    return propertyObj.p_max_area_after_far
def getFar(zoning_obj):
    return zoning_obj.zoning_far
def getLotCoverage(zoning_obj):
    return zoning_obj.zoning_lot_coverage
def getFrontSetBack(zoning_obj):
    return zoning_obj.zoning_min_front_setback
def getSideSetBack(zoning_obj):
    return zoning_obj.zoning_min_side_setback
def getRearSetBack(zoning_obj):
    return zoning_obj.zoning_min_rear_setback
# Additional API Functions
def getBuildingHeight(zoning_obj):
    return zoning_obj.zoning_building_height
def getFrontage(zoning_obj):
    return zoning_obj.zoning_min_frontage
def getParkingCap(zoning_obj):
    return zoning_obj.zoning_parking_capacity
def getStructureType(zoning_obj):
    return zoning_obj.structure_type

def callAppropriateSubFunctionLLM(coi,reqs_type):
    print(coi)
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
		
		
		
		
		
load_dotenv(find_dotenv())

# System prompt
system_initial_prompt = """
                You are a real estate expert able to understand user queries and extract the address from their prompt.

                Your task will be to extract the address, the type of request from the user as well as the concept of interest.

                In simple words, you need to reformulate the request in JSON format with three keys:
                - "address"
                - "request_type"
                - "concepts_of_interest"

                You need to identify the request_type, which must only be one of the following at all cost:
                {request_types}
                
                Always enclose the JSON code between [BEGIN] and [END] tags.
                
                A few examples:
                {example_user_prompts}

                It is important that your answers are accurate and that you strictly respect the required format. Take a deep breath, you can do it :) 
                """

request_types = """
                - "lot_subdivision", when the user wants to calculate a maximized parcel subdivision for a plot of land.
                - "zoning", when the user wants to get information about what is authorized on a parcel as per the regulation and land development code requirements.
                - "plan_recommendation", when the user wants suggestions of plans that could qualify for their parcel. 
                - "profitability", when the user wants to get advice on how to optimize profit out of a construction project on a given parcel.
                - "cost_estimation", when the query is about estimating the cost of a potential construction project.
                - "plan_compliance", when the user wants to upload a plan and pre-determine its legal compliance.
                - "other", any other type of request.
                ]
                """

example_user_prompts = """
                        Example input 1: 'What is the lot coverage and the side yard setback for 2101 Verbena St Nw Atlanta, GA 30314 ?

                        Example output 1: 
                        {{
                                "address": "2101 Verbena St Nw Atlanta, GA 30314",
                                "request_type": "zoning",
                                "concepts_of_interest": ["lot coverage", "side yard setback"]
                        }}

                        Example input 2: "I have a parcel, I'd like to estimate the cost of my project please help.
                        
                        Example output 2: 
                        {{
                                "address": "NA",
                                "request_type": "cost_estimation",
                                "concepts_of_interest": "cost"
                        }}

                        """

llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125",temperature=0)

def get_user_request(input,llm):
    '''
    Fetches the user request in JSON format.

    Inputs:
            input (string) containing user request.
    Output:
            json format representation of user request    
    '''

    # Prepare System and Human messages for LLMChain
    chat_messages = [
                        ('system',system_initial_prompt),
                        ('human', "{input}")
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    llmchain = LLMChain(llm=llm, prompt=prompt_template)

    # Run LLM chain based on the entries
    results = llmchain.run({"input":input,"request_types": request_types, "example_user_prompts":example_user_prompts})

    return results

def extract_substring(input_string):
    '''
    Function to extract json component only.

    input: input_string (string), with LLM response to user.
    output: substring (string), trimming out the start and end tags.
    '''
    begin_index = input_string.find("[BEGIN]")
    end_index = input_string.find("[END]")

    # Check if both substrings are present
    if begin_index == -1 or end_index == -1 or end_index <= begin_index:
        return input_string  # Return the original string if conditions are not met

    # Extract the substring
    begin_index += len("[BEGIN]")
    substring = input_string[begin_index:end_index]

    return substring

def generate_json_response(input):
    '''
    Function to generate the JSON response.

    input: input (string), contains the user request.
    output: json_response (dict), translation of the user prompt to json.  
    '''
    response = extract_substring(get_user_request(input,llm))
    try:
        json_response = json.loads(response)
        json_response['user_prompt'] = input

    except json.JSONDecodeError:
        json_response = {
                            "error_message": "Couldn't generate a valid JSON response for that input.",
                            "input": input,
                            "response": response
                        }
    return json_response

def final_response(final_response):
    '''
    generates response to user prompt.

    input:
            final_response (dict) containing the 'user_prompt' and 'results' from DB query.
    
    output:
            llm_response (string), generated text from LLM.
    
    '''
    final_system_prompt = """
                            You are a real estate expert, specialized in land development topics.
                            Please respond to the user using this context for {address}:
                            {results}

                            Be strict and accurate to the provided context. If you do not have information about one of the user's question, just say so.
                            """
        
    # Prepare System and Human messages for LLMChain
    chat_messages = [
                        ('system',final_system_prompt),
                        ('human', "{input}")
                    ]

    # Generate prompt template from messages
    prompt_template = ChatPromptTemplate.from_messages(chat_messages)

    # Create LLM chain with selected LLM and prepared dynamic template
    llmchain = LLMChain(llm=llm, prompt=prompt_template)
    # Run LLM chain based on the entries
    llm_response = llmchain.run({"input":final_response['user_prompt'],"results": final_response['results'],"address":final_response["address"]}) 

    return llm_response   
	

user_input = 'Give me wood for 8226 E 34th St, Atlanta, GA'
json_response = generate_json_response(user_input)
print(json_response['concepts_of_interest'],json_response['request_type'],json_response['address'])


address_str = json_response['address'].upper()
if(verfiyAddress(address_str)):
    print('User Address : ',address_str)
    address_parts = address_str.split(',', 1)
    address_p1 = address_parts[0]
    address_p2 = address_parts[1]
    attom_resp_json = callAttomPropertyAPI(address_p1,address_p2)
    if (attom_resp_json!=False):
        propertyObj = getPropertyObjFromAttomPropertyResponse(attom_resp_json)
        zoning_obj = getZoningInfoFromLLM(propertyObj.p_state,propertyObj.p_city,propertyObj.p_zoning_classification)
        propertyObj.setMaxAreaAfterFar(zoning_obj.zoning_far)
    else:
        print('Sorry, but I was unable to understand your address. Could you please specify it one more time ?')
else:
    print('Sorry, I am not able to process requests for this city yet. Please do not hesitate to contact us to know more about our future deployments.')

if (type(json_response['concepts_of_interest']) is list):
    for coi_val in json_response['concepts_of_interest']:
        resp = (callAppropriateSubFunctionLLM(coi_val,json_response['request_type']))
elif (type(json_response['concepts_of_interest']) is str):
    resp = (callAppropriateSubFunctionLLM(json_response['concepts_of_interest'],json_response['request_type']))

json_response['results'] = resp
final_response(json_response)
	
