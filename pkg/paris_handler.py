import os
from pkg.beetrack_api import BeetrackAPI
from pkg.commons import ignore_none_value, fetch_tag_value

class ParisHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get("paris_api_key")
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

    def create_paris_dispatches(self, spread_route):
        spread_dispatches = spread_route.get("response").get("route").get("dispatches")
        paris_dispatches = ignore_none_value(spread_dispatches)
        for dispatch in paris_dispatches:
            id_route_spread = dispatch.get("route_id")
            id_dispatch_paris = dispatch.get("dispatch_id")
            dispatch.update({'tags': [{"name": "id_route_spread","value": id_route_spread},
            {"name": "id_dispatch_paris","value": id_dispatch_paris}]})
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
        guide_id = self.body.get("guide") 
        substatus = self.homologate_substatus()
        if substatus == True:
            payload = {
            "status" : int(status)
        }
        else:
            payload = {
                "status" : int(status),
                "substatus_code" : substatus
            }
        create = BeetrackAPI(self.api_key).update_dispatch(guide_id, payload)
        print({"Beetrack Response" : create},{"Payload to update" : payload})
        return create

    def finish_route(self, ended_at, route_id, tag_route):
        payload = {
            "ended_at" : ended_at
        }
        filter_tag = BeetrackAPI.filter_dispatch(self, tag_route, route_id)
        paris_id_route = filter_tag.get("response")[0].get("route_id")
        route_finish = BeetrackAPI.update_route(self, paris_id_route, payload)
        return route_finish

    def update_trunk_dispatch(self):
        status = self.body.get("status")
        guide = self.body.get("guide")
        #tags = self.body.get("tags")
        #id_dispatch_paris = fetch_tag_value(tags, "id_dispatch_paris")
        payload = {
            "identifier" : guide,
            "status" : int(status),
            "place":  "CT Spread"
        }
        print(payload)
        update = BeetrackAPI(self.api_key).update_dispatch(guide, payload)
        print({"Request payload" : payload},{"Beetrack Response" : update})
        return update

    def homologate_substatus(self):
        status = self.body.get("status")
        substatus_code = self.body.get("substatus")
        sc = substatus_code
        if sc == None:
            print("Not substatus code to homologate or not homologation for the substatus code")
            return True
        else:
            if status == 2 and sc == "Entrega exitosa":
                print("Substatus Homologation : En Cliente")
                return 61
            elif status == 3 and sc == "Sin Moradores":
                print("Substatus Homologation : Cliente No Está")
                return 3
            elif status == 3 and sc == "No se encuentra direccion":
                print("Substatus Homologation : Dirección Errónea")
                return 2
            elif status == 3 and (sc == "Dificultad para llegar a domicilio" or sc == "Recibe en segunda visita" or sc == "Otro tipo de problema (describir)" or sc == "Fuera de Rango" or sc == "No se encuentra direccion"):
                print("Substatus Homologation : Motivos Transporte")
                return 6
            elif status == 3 and sc == "Domicilio no corresponde":
                print("Substatus Homologation : Motivos Cliente")
                return 30
            elif status == 3 and sc == "Anulará, incompleto o cambiado":
                print("Substatus Homologation : Expectativa")
                return 51
            elif status == 3 and sc == "Producto dañado":
                print("Substatus Homologation : Daño Producto")
                return 52
            elif status == 3 and sc == "Producto No Corresponde":
                print("Substatus Homologation : Producto No Corresponde")
                return 53
            elif status == 3 and sc == "Dirección Errónea - Definitivo":
                print("Substatus Homologation : Dirección Errónea - Definitivo")
                return 92
            elif status == 3 and sc == "Cliente No Está - Definitivo":
                print("Substatus Homologation : Cliente No Está - Definitivo")
                return 93
            elif status == 3 and sc == "Motivos Cliente - Definitivo":
                print("Substatus Homologation : Motivos Cliente - Definitivo")
                return 930
            elif status == 3 and (sc == "Motivos Transporte - Definitivo" or sc == "Robado" or sc == "Extraviado"):
                print("Substatus Homologation : Motivos Transporte - Definitivo")
                return 96
            elif status == 3 and sc == "Nota de Crédito":
                print("Substatus Homologation : Nota de Crédito")
                return 55
            elif status == 3 and sc == "Error sistémico":
                print("Substatus Homologation : Error sistémico")
                return 31
            elif status == 4 and sc == "Expectativa":
                print("Substatus Homologation : Expectativa")
                return 51
            elif status == 4 and sc == "Daño Producto":
                print("Substatus Homologation : Daño Producto")
                return 52
            elif status == 4 and sc == "Producto No Corresponde":
                print("Substatus Homologation : Producto No Corresponde")
                return 53
            else: 
                print("Not substatus code to homologate or not homologation for the substatus code")

    

