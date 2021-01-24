import os, redis
from datetime import timedelta
from time import sleep
from .beetrack_api import BeetrackAPI
from .commons import fetch_tag_value

class SpreadHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get('spread_api_key')
        self.base_url = "https://app.beetrack.com/api/external/v1"
        BeetrackAPI.__init__(self, self.api_key, self.base_url)
        url = os.environ.get('redis_url')
        port = os.environ.get('redis_port')
        self.connection = redis.Redis(host= url, port= port)

    def check_or_create_trucks(self, truck):
        get_trucks = BeetrackAPI.get_trucks(self)
        trucks = get_trucks.get('response').get('trucks')
        if truck not in trucks:
            print({'Handler New Truck': truck})
            new_truck = {'identifier' : truck}
            create = BeetrackAPI.create_truck(self,new_truck)
            print({"Message: Truck created in Spread": create})
            return truck
        else:
            return truck

    def get_spread_trunk_dispatches(self, paris_route):
        paris_dispatches = paris_route.get('response').get('route').get('dispatches')
        print("Paris dispatches :", paris_dispatches)
        spread_dispatches = []
        for dispatch in paris_dispatches:
            if dispatch.get('is_trunk') == True:  
                id_route_paris = dispatch.get('route_id')
                dispatch_indetifier = dispatch.get('identifier')
                dispatch.update({'tags': [{'id_route_paris': id_route_paris}]})
                dispatch.update({'identifier': 'PAR-'+str(dispatch_indetifier)})
                dispatch.pop('route_id')
                dispatch.pop('status')
                dispatch.pop('status_id')
                dispatch.pop('substatus')
                dispatch.pop('substatus_code')
                dispatch.pop('arrived_at')
                dispatch.pop('min_delivery_time')
                dispatch.pop('max_delivery_time')
                dispatch.pop('beecode')
                dispatch.pop('is_trunk')
                dispatch.update({'place' : 'CT Spread'})
                dispatch.update({'is_trunk': 'true'})
                dispatch.update({'destination': 'CT Spread'})
                items = dispatch.get('items')
                for item in items:
                    extras = item.get('extras')
                    carton_id = fetch_tag_value(extras, 'CARTONID')
                    item.update({'extras' : [{'CARTONID': carton_id}]})
                spread_dispatches.append(dispatch)
            else: 
                pass
        return spread_dispatches
        
    def create_new_trunk_route(self, truck, dispatches):
        date = self.body.get('date')
        id_route_paris = self.body.get('route')
        payload = {
            'truck_identifier': truck, 
            'date': date,
            'dispatches': dispatches
        }
        print({"New Trunk Route Payload": payload})
        create_route = BeetrackAPI.create_route(self,payload)
        id_route_spread = create_route.get('response').get('route_id')
        route = self.connection.setex(str(id_route_paris), 60*30, str(id_route_spread))
        # Cambiar tiempo a 24 hrs. (1 day)
        redis_save = {"identifier" : id_route_paris  , "redis": route}
        print ({"Redis Save Response" : redis_save})
        return create_route

    def get_id_dispatch_spread(self):
        guide = self.body.get('guide')
        guide_in_spread = 'PAR-'+str(guide)
        id_dispatch = self.body.get('dispatch_id')
        payload = {
            'is_trunk': True,
            'tags': [{'id_dispatch_paris': id_dispatch}]
        }
        print ({"Updating ID Dispatch Payload" : payload})
        update_dispatch = BeetrackAPI.update_dispatch(self, guide_in_spread, payload)
        return update_dispatch

    def verify_existence_in_spread(self):
        guide = self.body.get('guide')
        guide_in_spread = 'PAR-'+str(guide)
        print(guide_in_spread)
        fetch_dispatch = BeetrackAPI.get_dispatch(self, guide_in_spread)
        print(fetch_dispatch)
        response_mesage = fetch_dispatch.get('message')
        print(response_mesage)
        if response_mesage == "Not found":
            print({"Dispatch Information" : response_mesage})
            return False
        else:
            print({"Dispatch Information" : "Found"})
            return

    def add_dispatch_to_trunk_route(self):
        self.body.pop('resource')
        self.body.pop('event')
        self.body.pop('account_name')
        self.body.pop('account_id')
        self.body.pop('guide')
        paris_route_id = self.body.get('route_id')
        dispatch_identifier = 'PAR-' + self.body.get('identifier')
        self.body.update({'identifier' : dispatch_identifier})
        self.body.pop('route_id')
        paris_dispatch_id = self.body.get('dispatch_id')
        self.body.pop('dispatch_id')
        self.body.pop('truck_identifier')
        self.body.update({'tags': [{'id_route_paris': paris_route_id},{'id_dispatch_paris': paris_dispatch_id}]})
        items = self.body.get('items')
        for item in items:
            extras = item.get('extras')
            carton_id = fetch_tag_value(extras, 'CARTONID')
            item.update({'extras' : [{'CARTONID': carton_id}]})
            item.pop('id')
            item.pop('original_quantity')
            item.pop('delivered_quantity')
        spread_route_id = (self.connection.get(str(paris_route_id))).decode('ascii')
        print({"Spread route id from Redis" : spread_route_id})
        self.body.update({'route_id' : spread_route_id})
        payload = self.body
        print(payload)
        add_dispatch_on_spread = BeetrackAPI.create_dispatch(self, payload)
        return add_dispatch_on_spread

        
                





