import os
from pkg.beetrack_api import BeetrackAPI
from pkg.commons import ignore_none_value

class ParisHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get("paris_api_key")
        BeetrackAPI.__init__(self, self.api_key)

    def check_or_create_trucks(self, truck):
        get_trucks = BeetrackAPI.get_trucks(self)
        trucks = get_trucks.get('response').get('trucks')
        print(trucks)
        if truck not in trucks:
            print({"Handler New Truck": truck})
            new_truck = {"identifier" : truck}
            create = BeetrackAPI.create_truck(self,new_truck)
            print({"Beetrack Response" : create})
            return truck
        else:
            return truck

    def create_paris_dispatches(self, spread_route):
        # Agregar el parametro route_id para hacer el intercambio de identificadores.
        spread_dispatches = spread_route.get("response").get("route").get("dispatches")
        paris_dispatches = ignore_none_value(spread_dispatches)
        for dispatch in paris_dispatches:
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

    def create_new_route(self, truck, dispatches):
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

    def start_route(self, route_id, started_at):
        payload = {
            "started_at": started_at
        }
        route_start = BeetrackAPI.update_route(self,route_id, payload)
        print ({"Beetrack Response for Starting Route" : route_start})
        return route_start

    def update_dispatch(self):
        status = self.body.get("status")
        #substatus_code = body.get("substatus_code")
        guide_id = self.body.get("guide") 
        # Esta sujeto a que si Spread utilizara el mismo identificador o nombre de guia que Paris, en el caso que no
        # crear un  tag donde se guarde el identificador de Paris.
        payload = {
            "status" : int(status)
        }
        #"substatus_code" : substatus_code
        create = BeetrackAPI(self.api_key).update_dispatch(guide_id, payload)
        print({"Beetrack Response" : create})
        return create
