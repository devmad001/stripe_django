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