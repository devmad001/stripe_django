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