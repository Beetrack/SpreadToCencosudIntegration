import os, redis
from datetime import timedelta
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
            print({"Truck Doesn't Exist in Spread": truck})
            new_truck = {'identifier' : truck}
            create = BeetrackAPI.create_truck(self,new_truck)
            print({"Truck Create Response": create})
            return truck
        else:
            print({"Truck Already Exits in Spread" : truck})
            return truck

    def get_spread_trunk_dispatches(self, paris_route):
        paris_dispatches = paris_route.get('response').get('route').get('dispatches')
        fetch_response = []
        spread_dispatches = []
        for dispatch in paris_dispatches:
            if dispatch.get('is_trunk') == True:  
                id_route_paris = dispatch.get('route_id')
                dispatch_indetifier = dispatch.get('identifier')
                dispatch.update({'tags': [{'id_route_paris': id_route_paris}]})
                dispatch.update({'identifier': 'PAR'+str(dispatch_indetifier)})
                dispatch.pop('route_id')
                dispatch.pop('status')
                dispatch.pop('status_id')
                dispatch.pop('substatus')
                dispatch.pop('substatus_code')
                dispatch.pop('arrived_at')
                dispatch.pop('min_delivery_time')
                dispatch.pop('max_delivery_time')
                dispatch.pop('beecode')
                dispatch.update({'place' : 'CT Spread'})
                dispatch.update({'destination': 'CT Spread'})
                items = dispatch.get('items')
                for item in items:
                    extras = item.get('extras')
                    carton_id = fetch_tag_value(extras, 'CARTONID')
                    sku = fetch_tag_value(extras, 'SKU')
                    item.update(
                        {'extras' : [
                            {'CARTONID': carton_id},
                            {'SKU': sku}
                        ]
                        })
                spread_dispatches.append(dispatch)
                fetch_response.append(dispatch_indetifier)
            else: 
                fetch_response.append("{} doesn't belong".format(dispatch.get('identifier')))
        print({ "Dispatches Fetch Response" : fetch_response})
        return spread_dispatches
        
    def create_new_trunk_route(self, truck, dispatches):
        date = self.body.get('date')
        id_route_paris = self.body.get('route')
        payload = {
            'truck_identifier': truck, 
            'date': date,
            'dispatches': dispatches
        }
        print({"  New Trunk Route Payload": payload})
        create_route = BeetrackAPI.create_route(self, payload)
        if create_route.get('status') == "ok":
            id_route_spread = create_route.get('response').get('route_id')
            print({"  Response Create Route In Spread" : create_route})
            saving_route = self.connection.setex(str(id_route_paris), 60*60*24, str(id_route_spread))
            if saving_route:
                print({"    Redis Response": saving_route, "Key" : id_route_paris, "Value" : id_route_spread})
            else:
                print({"     Redis Response" : "Unable to save route on Redis"})
            return True
        else:
            return False

    def get_id_dispatch_spread(self):
        paris_route_id = self.body.get('route_id')
        spread_route_id = self.connection.get(str(paris_route_id))
        print({"  Get Spread Route Redis Response" : spread_route_id})
        if spread_route_id != False:
            print({"  Case" : "Adding dispatch_id to Spread dispatch"})
            guide = self.body.get('guide')
            guide_in_spread = 'PAR' + str(guide)
            is_trunk = self.body.get('is_trunk')
            is_pickup = self.body.get('is_pickup')
            id_dispatch = self.body.get('dispatch_id')
            tags = [{"id_dispatch_paris" : id_dispatch}]
            if self.body.get('is_pickup') == True:
                tags.append({"pick_up" : "true"})
            else:
                pass
            payload = {
                "route_id": spread_route_id.decode('ascii'),
                "is_trunk": is_trunk,
                "is_pickup": is_pickup,
                "tags":  tags
            }
            print ({"   Updating ID Dispatch Payload" : payload})
            update_dispatch = BeetrackAPI.update_dispatch(self, guide_in_spread, payload)
            return update_dispatch
        else: 
            print({"  Unable To Add id_ispatch" : "Paris route id not found in Redis"})
            return {"status" : "error"}

    def verify_existence_in_spread(self):
        guide = self.body.get('guide')
        guide_in_spread = 'PAR' + str(guide)
        print({" Dispatch Existance Verification" : guide_in_spread})
        fetch_dispatch = BeetrackAPI.get_dispatch(self, guide_in_spread)
        if fetch_dispatch.get('message') == "Not found":
            print({"  Dispatch" : response_mesage})
            add_dispatch_on_Spread_route = self.add_dispatch_to_trunk_route()
            print({"   Response For Add Dispatch In Trunk Route" : add_dispatch_on_Spread_route})
            if add_dispatch_on_Spread_route.get('status') == 'ok':
                return {"statusCode": 200, "body": "Message: Paris dispatch added correctly."}
            else:
                return {"statusCode": 404, "body": "Message: Unable to add Paris dispatch."}
        else:
            print({" Dispatch" : "Found"})
            update_dispatch_id_in_spread = self.get_id_dispatch_spread()
            print({"   Response For Update id_dispatch In Dispatch" : update_dispatch_id_in_spread})
            if update_dispatch_id_in_spread.get('status') == 'ok':
                return {"statusCode": 200, "body": "Message: Paris dispatch_id added correctly."}
            else:
                return  {"statusCode": 404, "body": "Message: Unable to update Paris id_dispatch."}

    def add_dispatch_to_trunk_route(self):
        paris_route_id = self.body.get('route_id')
        spread_route_id = self.connection.get(str(paris_route_id))
        print("  {Get Spread Route Redis Response" : spread_route_id})
        if spread_route_id != False:
            print({"  Case" : "Add Paris dispatch in clone trunk route"})
            self.body.update({'route_id' : spread_route_id.decode('ascii')})
            self.body.pop('resource')
            self.body.pop('event')
            self.body.pop('account_name')
            self.body.pop('account_id')
            self.body.pop('guide')
            self.body.pop('route_id')
            self.body.pop('truck_identifier')
            dispatch_identifier = 'PAR-' + self.body.get('identifier')
            self.body.update({'identifier' : dispatch_identifier})
            paris_dispatch_id = self.body.get('dispatch_id')
            self.body.pop('dispatch_id')
            tags = [{'id_route_paris': paris_route_id},{'id_dispatch_paris': paris_dispatch_id}]
            if self.body.get('is_pickup') == True:
                tags.append({"pick_up" : "true"})
            else:
                pass
            self.body.update({'tags': tags})
            items = self.body.get('items')
            for item in items:
                extras = item.get('extras')
                carton_id = fetch_tag_value(extras, 'CARTONID')
                item.update({'extras' : [{'CARTONID': carton_id}]})
                item.pop('id')
                item.pop('original_quantity')
                item.pop('delivered_quantity')
            payload = self.body
            print({"   Add Dispatch Payload" : payload})
            add_dispatch_on_spread = BeetrackAPI.create_dispatch(self, payload)
            return add_dispatch_on_spread
        else: 
            print({"  Unable To Add Dispatch" : "Paris route id not found in Redis"})
            return {"status" : "error"}
