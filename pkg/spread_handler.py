import os
from pkg.beetrack_api import BeetrackAPI

class SpreadHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get("spread_api_key")
        BeetrackAPI.__init__(self, self.api_key)

    def check_or_create_trucks(self, truck):
        get_trucks = BeetrackAPI.get_trucks(self)
        trucks = get_trucks.get('response').get('trucks')
        if truck not in trucks:
            print({"Handler New Truck": truck})
            new_truck = {"identifier" : truck}
            create = BeetrackAPI.create_truck(self,new_truck)
            print({"Beetrack Response" : create})
            return truck
        else:
            return truck

    def get_spread_trunk_dispatches(self, paris_route):
        # Agregar el parametro route_id para hacer el intercambio de identificadores.
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

    def create_new_trunk_route(self, truck, dispatches):
        date = self.body.get('date')
        print("Api key to create trunk route on Spread", self.api_key)
        print("Date for the trunk route on Spread:", date)
        print("Truck asigned to the trunk route on Spread :", truck)
        print("Dispatches added on trunk route on Spread", dispatches)
        payload = {
            "truck_identifier": truck, 
            "date": date,
            "dispatches": dispatches
        }
        create_route = BeetrackAPI.create_route(self,payload)
        print ({"Beetrack Response for Creating Route" : create_route})
        return create_route
