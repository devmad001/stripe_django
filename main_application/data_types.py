class plan_obj:
    area_total = 0
    bedrooms_count = 0
    bathrooms_count = 0
    bathrooms_full_count = 0
    bathrooms_half_count = 0
    stories = 0
    area_first_floor = 0
    area_second_floor = 0
    area_third_floor = 0
    area_basement = 0
    area_garage = 0
    cars_capacity = 0
    width = 0
    depth = 0
    buy_url = ''
    plan_number = ''
    title = ''
    image_link = ''
    architectural_style = ''
        
    def __init__(self,area_total,bedrooms_count,bathrooms_count,bathrooms_full_count,\
                 bathrooms_half_count,stories,area_first_floor,area_second_floor,\
                 area_third_floor,area_basement,area_garage,cars_capacity,width,depth,buy_url,\
                 plan_number,title,image_link):
        self.area_total = area_total
        self.bedrooms_count = bedrooms_count
        self.bathrooms_count = bathrooms_count
        self.bathrooms_full_count = bathrooms_full_count
        self.bathrooms_half_count = bathrooms_half_count
        self.stories = stories
        self.area_first_floor = area_first_floor
        self.area_second_floor = area_second_floor
        self.area_third_floor = area_third_floor
        self.area_basement = area_basement
        self.area_garage = area_garage
        self.cars_capacity = cars_capacity
        self.width = width
        self.depth = depth
        self.buy_url = buy_url
        self.plan_number = plan_number
        self.title = title
        self.image_link = image_link
        # self.architectural_style = architectural_style


class comp_obj:
    address = ''
    zillow_link = ''
    distance = 0.0
    value = 0.0
    area = 0
    bed_count = 0
    bath_count = 0.0
    year = 0
    lot_area = 0
    avm = 0
    price_per_sq_ft = 0.0
    deeds_sale_amount = 0.0
        
    def __init__(self,address,distance,area,bed_count,bath_count,year,lot_area,avm,price_per_sq_ft,deeds_sale_amount):
        self.address = address
        self.distance = round(distance,3)
        self.value = 0.0
        self.area = area
        self.bed_count = bed_count
        self.bath_count = bath_count
        self.year = year
        self.lot_area = lot_area
        self.avm = avm
        self.zillow_link = ''
        self.price_per_sq_ft = round(price_per_sq_ft,2)
        self.deeds_sale_amount = deeds_sale_amount
    def setValue(self,value):
        self.value = int(value)
    def print(self):
        print(self.address,',' ,self.distance,', ',self.area,', ',self.bed_count,\
              ',',self.bath_count,'',self.year,'',self.lot_area,',',self.value,\
              ',',self.avm,',',self.price_per_sq_ft,',',self.zillow_link)
    def setZillowLink(self):
        comp_addrs = self.address
        comp_addrs = comp_addrs.replace(',', '-')
        comp_addrs = comp_addrs.replace(' ', '-')
        self.zillow_link = 'https://www.zillow.com/homes/'+comp_addrs+'_rb/'

class userInputForm:
    min_area = 0
    max_area = 0
    bed_count = 0
    full_bath_count = 0
    half_bath_count = 0
    total_bath_count = 0
    story_count = 0
    garage_count = 0
    addr_city = ''
    addr_state = ''
    addr_county = ''
    build_quality = ''
    basement_type = ''
    acquisition_cost = 0
    home_style = ''
    complete_address = ''

    def __init__(self,min_area,max_area,bed_count,full_bath_count,half_bath_count,story_count,garage_count,\
                 build_quality,basement_type,acquisition_cost,home_style,complete_address):
        self.min_area = min_area
        self.max_area = max_area
        self.bed_count = bed_count
        self.full_bath_count = full_bath_count
        self.half_bath_count = half_bath_count
        self.total_bath_count = self.full_bath_count + 0.5*self.half_bath_count
        self.story_count = story_count
        self.garage_count = garage_count
        self.addr_city = ''
        self.addr_state = ''
        self.build_quality = build_quality
        self.basement_type = basement_type
        self.acquisition_cost = acquisition_cost
        self.home_style = home_style
        self.complete_address = complete_address


class queryPropertyForComps:
    year_build = 0
    area = 0
    area_basement = 0
    area_garage = 0
    baths_full = 0
    baths_half = 0
    bedrooms = 0
    vac = 0
    vac2 = 0
    def __init__(self,year_build,area,area_basement,area_garage,baths_full,baths_half,bedrooms):
        self.year_build = int(year_build)
        self.area = int(area)
        self.area_basement = int(area_basement)
        self.area_garage = int(area_garage)
        self.baths_full = int(baths_full)
        self.baths_half = int(baths_half)
        self.bedrooms = int(bedrooms)
    def setVAC(self,vac):
        self.vac = vac
    def setVAC2(self,vac2):
        self.vac2 = vac2
    def print(self):
        print('Year build : ',self.year_build)
        print('Area : ',self.area)
        print('Area Basement: ',self.area_basement)
        print('Area Garage : ',self.area_garage)
        print('Baths-full : ',self.baths_full)
        print('Bath-half : ',self.baths_half)
        print('Bedrooms : ',self.bedrooms)
        print('VAC : ',self.vac)

class KPI:
    vac = 0
    vac2 = 0
    construction_cost = 0
    total_project_cost = 0
    acquisition_cost = 0
    equity = 0
    equity2 = 0
    price_psqft_finished = 0
    price_psqft_unfinished = 0
    def __init__(self,vac,vac2,construction_cost,acquisition_cost,price_psqft_finished):
        self.vac = int(vac)
        self.vac2 = int(vac2)
        self.construction_cost = int(construction_cost)
        self.acquisition_cost = int(acquisition_cost)
        self.total_project_cost = self.construction_cost + self.acquisition_cost
        self.equity = self.vac - self.total_project_cost
        self.equity2 = self.vac2 - self.total_project_cost
        self.price_psqft_finished = round(price_psqft_finished,3)
        self.price_psqft_unfinished = round(self.price_psqft_finished * 0.55,3)
        
    def print(self):
        print('KPIs')
        print('VAC : ',self.vac)
        print('Construction Cost : ',self.construction_cost)
        print('Total Project Cost : ',self.total_project_cost)
        print('Equity : ', self.equity )

    def setConstructionCost(self,construction_cost):
        self.construction_cost = int(construction_cost)
        self.total_project_cost = self.construction_cost + self.acquisition_cost
        self.equity = self.vac - self.total_project_cost
        self.equity2 = self.vac2 - self.total_project_cost

    def setVACbasedonQuality(self,vac,vac2,build_quality):
        self.vac = int(vac)
        self.vac2 = int(vac2)
        if(build_quality=='SILVER'):
            self.vac = self.vac + self.vac*0.08
            self.vac2 = self.vac2 + self.vac2*0.08
        if(build_quality=='GOLD'):
            self.vac = self.vac + self.vac*0.15
            self.vac2 = self.vac2 + self.vac2*0.15
        self.vac = int(self.vac)
        self.vac2 = int(self.vac2)
        self.equity = self.vac - self.total_project_cost
        self.equity2 = self.vac2 - self.total_project_cost