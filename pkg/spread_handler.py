import os
from pkg.beetrack_api import BeetrackAPI

class SpreadHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get("spread_group_api_key")
        BeetrackAPI.__init__(self, self.api_key)

    def check_or_create_trucks(self, truck):
        get_trucks = BeetrackAPI.get_trucks(self)
        trucks = get_trucks.get('response').get('trucks')
        print(trucks)
        print("API KEY COCT: ", self.api_key)
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
            if dispatch.get("destination").get("name") == "CT Spread" and dispatch.get("is_trunk") == "true":  
                id_route_paris = dispatch.get("route_id")
                dispatch.update({'tags': [{"name": "id_route_paris","value": id_route_paris}]})
                dispatch.pop('route_id')
                dispatch.pop('status')
                dispatch.pop('status_id')
                dispatch.pop('substatus')
                dispatch.pop('substatus_code')
                dispatch.pop('arrived_at')
                dispatch.pop('min_delivery_time')
                dispatch.pop('max_delivery_time')
                dispatch.pop('beecode')
        return paris_dispatches

    def create_new_trunk_route(self, truck, dispatches):
        date = self.body.get('date')
        print(self.api_key)
        print(date)
        print(truck)
        print(dispatches)
        payload = {
            "truck_identifier": truck, 
            "date": date,
            "dispatches": dispatches
        }
        create_route = BeetrackAPI.create_route(self,payload)
        print ({"Beetrack Response for Creating Route" : create_route})
        return create_route
