import os
from pkg.beetrack_api import BeetrackAPI

class SpreadHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get("spread_api_key")
        BeetrackAPI.__init__(self, self.api_key)

    def check_or_create_trucks(self, truck, account_id):
        get_trucks = BeetrackAPI.get_trucks(self, account_id)
        trucks = get_trucks.get('response').get('trucks')
        if truck not in trucks:
            print({"Handler New Truck": truck})
            new_truck = {"identifier" : truck}
            create = BeetrackAPI.create_truck(self,new_truck, account_id)
            print({"Beetrack Response" : create})
            return truck
        else:
            return truck

    def get_spread_trunk_dispatches(self, paris_route):
        paris_dispatches = paris_route.get("response").get("route").get("dispatches")
        for dispatch in paris_dispatches:
            if dispatch.get("destination").get("name") == "CT Spread" and dispatch.get("is_trunk") == True:  
                id_route_paris = dispatch.get("route_id")
                id_dispatch_paris = dispatch.get("dispatch_id")
                dispatch.update({'tags': [{"name": "id_route_paris","value": id_route_paris},{"name": "id_dispatch_paris","value": id_dispatch_paris}]})
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
                dispatch.update({'is_trunk': 'true'})
                dispatch.update({'destination': 'CT Spread'})
        return paris_dispatches

    def create_new_trunk_route(self, truck, dispatches, account_id):
        date = self.body.get('date')
        payload = {
            "truck_identifier": truck, 
            "date": date,
            "dispatches": dispatches
        }
        print({"New Trunk Route Payload": payload})
        create_route = BeetrackAPI.create_route(self,payload, account_id)
        print ({"Beetrack Response for Creating Route" : create_route})
        return create_route

    def get_id_dispatch_spread(self, account_id):
        guide = self.body.get("guide")
        id_dispatch = self.body.get("dispatch_id")
        payload = {
            "is_trunk": True,
            "tags": [{"name": "id_dispatch_paris","value": id_dispatch}]
        }
        print ({"Updating ID Dispatch Payload" : payload})
        update_dispatch = BeetrackAPI.update_dispatch(self, guide, payload, account_id)
        return update_dispatch