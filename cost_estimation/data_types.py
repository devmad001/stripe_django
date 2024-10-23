class KPI:
    vac_min = 0
    vac_max = 0
    construction_cost = 0
    total_project_cost = 0
    acquisition_cost = 0
    equity_min = 0
    equity_max = 0
    price_psqft_finished = 0
    price_psqft_unfinished = 0
    area_finished = 0
    area_unfinished = 0
    construction_cost_finished = 0
    construction_cost_unfinished = 0
    construction_cost_extra = 0
    def __init__(self,vac_min,vac_max,construction_cost,acquisition_cost,price_psqft_finished):
        self.vac_min = int(vac_min)
        self.vac_max = int(vac_max)
        self.construction_cost = int(construction_cost)
        self.acquisition_cost = int(acquisition_cost)
        self.total_project_cost = self.construction_cost + self.acquisition_cost
        self.equity_min = self.vac_min - self.total_project_cost
        self.equity_max = self.vac_max - self.total_project_cost
        self.price_psqft_finished = round(price_psqft_finished,3)
        self.price_psqft_unfinished = round(self.price_psqft_finished * 0.55,3)
        self.area_finished = 0
        self.area_unfinished = 0
        self.construction_cost_finished = 0
        self.construction_cost_unfinished = 0
        self.construction_cost_extra = 0
        
    def print(self):
        print('KPIs')
        print('VAC : ',self.vac_min)
        print('Construction Cost : ',self.construction_cost)
        print('Total Project Cost : ',self.total_project_cost)
        print('Equity : ', self.equity_min )

    def setConstructionCost(self,construction_cost):
        self.construction_cost = int(construction_cost)
        self.total_project_cost = self.construction_cost + self.acquisition_cost
        self.equity_min = self.vac_min - self.total_project_cost
        self.equity_max = self.vac_max - self.total_project_cost

    def setLandAcquisitionCost(self,land_cost):
        self.acquisition_cost = int(land_cost)
        self.total_project_cost = self.construction_cost + self.acquisition_cost
        self.equity_min = self.vac_min - self.total_project_cost
        self.equity_max = self.vac_max - self.total_project_cost 

    def setVACbasedonQuality(self,vac,vac2,build_quality):
        self.vac_min = int(vac)
        self.vac_max = int(vac2)
        if(build_quality=='SILVER'):
            self.vac_min *= 1.08
            self.vac_max *= 1.08
        if(build_quality=='GOLD'):
            self.vac_min *= 1.15
            self.vac_max *= 1.15
        self.vac_min = int(self.vac_min)
        self.vac_max = int(self.vac_max)
        self.equity_min = self.vac_min - self.total_project_cost
        self.equity_max = self.vac_max - self.total_project_cost

    def setFinishedAndUnfinishedValues(self,finished_area,unfinshed_area):
        self.area_finished = finished_area
        self.area_unfinished = unfinshed_area
        self.construction_cost_finished = round(self.area_finished * self.price_psqft_finished,0)
        self.construction_cost_unfinished = round(self.area_unfinished * self.price_psqft_unfinished,0)
        self.construction_cost_extra = round(self.construction_cost - \
                                             (self.construction_cost_finished+self.construction_cost_unfinished),0)



class Comparable:
    address = ''
    zillow_link = ''
    distance = 0.0
    value = 0.0
    area = 0
    bed_n = 0
    full_bath_n = 0.0
    half_bath_n = 0.0
    story_n = 0
    garage_area = 0
    basement_area_total = 0
    basement_area_finished = 0
    basement_area_unfinished = 0
    year = 0
    lot_area = 0
    avm = 0
    price_per_sq_ft = 0.0
    deeds_sale_amount = 0.0
    has_fireplace = False
    has_pool = False
        
    def __init__(self,address,distance,area,bed_count,bath_count_full,bath_count_half,story_count,\
                 year,lot_area,garage_area,basement_area_total,basement_area_finished,basement_area_unfinished,\
                    price_per_sq_ft,deeds_sale_amount,has_fireplace=False,has_pool=False):
        self.address = address
        self.distance = round(distance,3)
        self.value = 0.0
        self.area = area
        self.bed_n = bed_count
        self.full_bath_n = bath_count_full
        self.half_bath_n = bath_count_half
        self.story_n = story_count
        self.year = year
        self.lot_area = lot_area
        self.garage_area = garage_area
        self.basement_area_total = basement_area_total
        self.basement_area_finished = basement_area_finished
        self.basement_area_unfinished = basement_area_unfinished
        self.zillow_link = ''
        self.price_per_sq_ft = round(price_per_sq_ft,2)
        self.deeds_sale_amount = deeds_sale_amount
        self.has_fireplace = has_fireplace
        self.has_pool = has_pool
    def setValue(self,value):
        self.value = int(value)
    def print(self):
        print(self.address,',' ,self.distance,', ',self.area,', ',self.bed_n,\
              ',',self.full_bath_n,',',self.year,',',self.lot_area,',',self.deeds_sale_amount,\
              ',',self.price_per_sq_ft,',',self.zillow_link)
    def setZillowLink(self):
        comp_addrs = self.address
        comp_addrs = comp_addrs.replace(',', '-')
        comp_addrs = comp_addrs.replace(' ', '-')
        self.zillow_link = 'https://www.zillow.com/homes/'+comp_addrs+'_rb/'


class ArchitecturalPlan:
    area_total = 0
    bedrooms_n = 0
    bathrooms_n = 0
    bathrooms_full_n = 0
    bathrooms_half_n = 0
    story_n = 0
    area_first_floor = 0
    area_second_floor = 0
    area_third_floor = 0
    area_basement = 0
    area_garage = 0
    cars_n = 0
    garage_location = ''
    garage_type = ''
    width = 0
    depth = 0
    height = 0
    units_n = 0
    buy_url = ''
    plan_number = ''
    title = ''
    image_link = ''
    architectural_style = ''
    foundation = ''
    exterior_wall_type = ''

        
    def __init__(self,area_total,bedrooms_count,bathrooms_count,bathrooms_full_count,\
                 bathrooms_half_count,stories,area_first_floor,area_second_floor,\
                 area_third_floor,area_basement,area_garage,cars_capacity,garage_location,\
                 garage_type,width,depth,height,units,buy_url,plan_number,title,image_link,\
                 architectural_style,foundation,exterior_wall_type):
        self.area_total = area_total
        self.bedrooms_n = bedrooms_count
        self.bathrooms_n = bathrooms_count
        self.bathrooms_full_n = bathrooms_full_count
        self.bathrooms_half_n = bathrooms_half_count
        self.story_n = stories
        self.area_first_floor = area_first_floor
        self.area_second_floor = area_second_floor
        self.area_third_floor = area_third_floor
        self.area_basement = area_basement
        self.area_garage = area_garage
        self.cars_n = cars_capacity
        self.garage_location = garage_location
        self.garage_type = garage_type
        self.width = width
        self.depth = depth
        self.height = height
        self.units_n = units
        self.buy_url = buy_url
        self.plan_number = plan_number
        self.title = title
        self.image_link = image_link
        self.architectural_style = architectural_style
        self.foundation = foundation
        self.exterior_wall_type = exterior_wall_type


class Property:
    attom_id = ''
    cord = []
    lat = 0.0
    lng = 0.0
    area = 0.0
    school_dist = ''
    tax_amount = 0
    city = ''
    state = ''
    county = ''
    street_adr = ''
    query_address = ''
    parcel_id = ''
    depth = 0
    width=0
    depth_after_zoning = 0
    width_after_zoning = 0
    area_after_zoning = 0
    max_area_after_far = 0
    type = ''
    zoning_classification = ''
    zoning_dscrp = ''
    owner_name = ''
    land_cost = 0
    
    def __init__(self,p_attom_id,p_cord,p_lat,p_lng,p_area,p_school_dist,p_tax_amount,\
                p_city,p_state,p_county,p_street_adr,p_query_address,p_parcel_id,\
                p_type,p_zoning_classification,p_zoning_dscrp,p_owner_name,p_land_cost):
        self.attom_id = p_attom_id
        self.cord = p_cord
        self.lat = p_lat
        self.lng = p_lng
        self.area = p_area
        self.school_dist = p_school_dist
        self.tax_amount = p_tax_amount
        self.city = p_city
        self.state = p_state
        self.county = p_county
        self.street_adr = p_street_adr
        self.query_address = p_query_address
        self.parcel_id = p_parcel_id
        self.depth = 0
        self.width=0
        self.depth_after_zoning = 0
        self.width_after_zoning = 0
        self.area_after_zoning = 0
        self.max_area_after_far = 0
        self.type = p_type
        self.zoning_classification = p_zoning_classification
        self.zoning_dscrp = p_zoning_dscrp
        self.owner_name = p_owner_name
        self.land_cost = p_land_cost

    def setMaxAreaAfterFar(self,far):
        print(far,self.area)
        self.max_area_after_far = far*self.area
        print('Area after far : ',self.max_area_after_far)
    def setSchoolDistrict(self,school_district):
        self.school_dist = school_district