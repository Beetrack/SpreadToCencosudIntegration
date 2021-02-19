import os
from .beetrack_api import BeetrackAPI
from .commons import ignore_none_value, fetch_tag_value

class ParisHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get('paris_api_key')
        self.base_url = 'https://app.beetrack.com/api/external/v1'
        BeetrackAPI.__init__(self, self.api_key, self.base_url)

    def update_dispatch(self):
        tags = self.body.get('tags')
        id_dispatch_paris = fetch_tag_value(tags, 'id_dispatch_paris')
        if id_dispatch_paris != None:
            print({"Update LastMile Dispatch" : self.body.get('identifier')})
            self.body.pop('resource')
            self.body.pop('event')
            self.body.pop('account_name')
            self.body.pop('account_id')
            self.body.pop('identifier')
            self.body.pop('route_id')
            self.body.pop('truck_identifier')
            self.body.pop('evaluation_answers')
            self.body.pop('groups')
            guide = self.body.get('guide')
            self.body.pop('guide')
            substatus = self.homologate_substatus()
            self.body.pop('substatus_code')
            self.body.update({'substatus' : substatus})
            items = self.body.get('items')
            for item in items:
                item.pop('id')
                item.pop('extras')
            self.body.update({'destination' : None})
            self.body.update({'place' : None})
            self.body.update({'dispatch_id' : int(id_dispatch_paris)})
            self.body.pop('tags')
            payload = self.body
            print({"Update Payload": payload})
            create = BeetrackAPI(self.api_key, self.base_url).update_dispatch(guide, payload)
            print({"Update LastMile Dispatch Response" : create})
            if create.get('status') == 'ok':
                return {"statusCode": 200, "body": "Message: Paris dispatch updated correctly."}
            else: 
                return {"statusCode": 400, "body": "Message: Unable to update Paris dispatch."}
        else:
            print({"Unable To Update Dispatch" : " Tag id_dispatch_paris not found."})
            return {"statusCode": 404, "body": "Message: Unable to update Paris dispatch."}

    def update_trunk_dispatch(self):
        status = self.body.get('status')
        guide = self.body.get('guide')
        guide_on_paris = guide.replace('PAR', '')
        tags = self.body.get('tags')
        pickup = self.body.get('is_pickup')
        id_dispatch_paris = fetch_tag_value(tags, 'id_dispatch_paris')
        if id_dispatch_paris != None:
            print({"Update Trunk Dispatch" : guide_on_paris})
            if pickup == True:
                payload = {
                    'status' : int(status),
                    'place':  'CT SPREAD',
                    'dispatch_id' : int(id_dispatch_paris),
                    'is_pickup' : True
                }
            else: 
                payload = {
                    'status' : int(status),
                    'place':  'CT SPREAD',
                    'dispatch_id' : int(id_dispatch_paris)
                }
            print({"  Update Payload" : payload})
            update = BeetrackAPI(self.api_key, self.base_url).update_dispatch(guide_on_paris, payload)
            print({"  Update Trunk Dispatch Response" : update})
            if update.get('status') == 'ok':
                return {"statusCode": 200, "body": "Message: Paris dispatch updated correctly."}
            else: 
                return {"statusCode": 400, "body": "Message: Unable to update Paris dispatch."}
        else:
            print({" Unable To Update Dispatch" : " Tag id_dispatch_paris not found."})
            return {"statusCode": 404, "body": "Message: Unable to update Paris dispatch."}

    def homologate_substatus(self):
        print({"Case Homologate Statuses" : self.body.get('identifier')})
        status = self.body.get('status')
        substatus_code = self.body.get('substatus')
        sc = substatus_code
        if sc == None:
            print("Not substatus code to homologate or not homologation for the substatus code")
            return None
        else:
            if status == 2 and sc == 'Entrega exitosa':
                print("Substatus Homologation : En Cliente")
                return 'En Cliente'
            elif status == 2 and sc == 'En Expedición (Click & Collect)':
                print("Substatus Homologation : En Expedición (Click & Collect)")
                return 'En Expedición (Click & Collect)'
            elif status == 2 and sc == 'Recogido En Expedición (Click & Collect)':
                print("Substatus Homologation : Recogido En Expedición (Click & Collect)")
                return 'Recogido En Expedición (Click & Collect)'
            elif status == 2 and sc == 'Recogido':
                print("Substatus Homologation : Recogido")
                return 'Recogido'
            elif status == 3 and sc == 'Rechazo en Expedición (Click & Collect)':
                print("Substatus Homologation : Rechazo en Expedición (Click & Collect)")
                return 'Rechazo en Expedición (Click & Collect)'
            elif status == 3 and sc == 'Sin Moradores':
                print("Substatus Homologation : Cliente No Está")
                return 'Cliente No Está'
            elif status == 3 and sc == 'No Recogido - Cliente No Está':
                print("Substatus Homologation : No Recogido - Cliente No Está")
                return 'No Recogido - Cliente No Está' 
            elif status == 3 and sc == 'No Recogido - Dirección erronea':
                print("Substatus Homologation : No Recogido - Dirección erronea")
                return 'No Recogido - Dirección erronea' 
            elif status == 3 and sc == 'No Recogido - Motivos Cliente':
                print("Substatus Homologation : No Recogido - Motivos Cliente")
                return 'No Recogido - Motivos Cliente'
            elif status == 3 and sc == 'No Recogido - Motivos Transporte':
                print("Substatus Homologation : No Recogido - Motivos Transporte")
                return 'No Recogido - Motivos Transporte'
            elif status == 3 and sc == 'No Recogido - No cumple condición':
                print("Substatus Homologation : No Recogido - No cumple condición")
                return 'No Recogido - No cumple condición'
            elif status == 3 and sc == 'No Recogido Cliente No Está - Definitivo':
                print("Substatus Homologation : No Recogido Cliente No Está - Definitivo")
                return 'No Recogido Cliente No Está - Definitivo'
            elif status == 3 and sc == 'No Recogido Dirección Errónea - Definitivo':
                print("Substatus Homologation : No Recogido Dirección Errónea - Definitivo")
                return 'No Recogido Dirección Errónea - Definitivo'
            elif status == 3 and sc == 'No Recogido Motivo Cliente - Defintivo':
                print("Substatus Homologation : No Recogido Motivo Cliente - Defintivo")
                return 'No Recogido Motivo Cliente - Defintivo'
            elif status == 3 and sc == 'No Recogido Motivo Transporte - Defintivo':
                print("Substatus Homologation : No Recogido Motivo Transporte - Defintivo")
                return 'No Recogido Motivo Transporte - Defintivo'
            elif status == 3 and sc == 'No se encuentra direccion':
                print("Substatus Homologation : Dirección Errónea")
                return 'Dirección Errónea'
            elif status == 3 and (sc == 'Dificultad para llegar a domicilio' or sc == 'Recibe en segunda visita' or sc == 'Otro tipo de problema (describir)' or sc == 'Fuera de Rango' or sc == 'No se encuentra direccion'):
                print('Substatus Homologation : Motivos Transporte')
                return 'Motivos Transporte'
            elif status == 3 and sc == 'Domicilio no corresponde':
                print("Substatus Homologation : Motivos Cliente")
                return 'Motivos Cliente'
            elif status == 3 and sc == 'Anulará, incompleto o cambiado':
                print("Substatus Homologation : Expectativa")
                return 'Expectativa'
            elif status == 3 and sc == 'Producto dañado':
                print("Substatus Homologation : Daño Producto")
                return 'Daño Producto'
            elif status == 3 and sc == 'Producto No Corresponde':
                print("Substatus Homologation : Producto No Corresponde")
                return 'Producto No Corresponde'
            elif status == 3 and sc == 'Dirección Errónea - Definitivo':
                print("Substatus Homologation : Dirección Errónea - Definitivo")
                return 'Dirección Errónea - Definitivo'
            elif status == 3 and sc == 'Cliente No Está - Definitivo':
                print("Substatus Homologation : Cliente No Está - Definitivo")
                return 'Cliente No Está - Definitivo'
            elif status == 3 and sc == 'Motivos Cliente - Definitivo':
                print("Substatus Homologation : Motivos Cliente - Definitivo")
                return 'Motivos Cliente - Definitivo'
            elif status == 3 and (sc == 'Motivos Transporte - Definitivo' or sc == 'Robado' or sc == 'Extraviado'):
                print("Substatus Homologation : Motivos Transporte - Definitivo")
                return 'Motivos Transporte - Definitivo'
            elif status == 3 and sc == 'Nota de Crédito':
                print("Substatus Homologation : Nota de Crédito")
                return 'Nota de Crédito'
            elif status == 3 and sc == 'Error sistémico':
                print("Substatus Homologation : Error sistémico")
                return 'Error sistémico'
            elif status == 4 and sc == 'Expectativa':
                print("Substatus Homologation : Expectativa")
                return 'Expectativa'
            elif status == 4 and sc == 'Daño Producto':
                print("Substatus Homologation : Daño Producto")
                return 'Daño Producto'
            elif status == 4 and sc == 'Producto No Corresponde':
                print("Substatus Homologation : Producto No Corresponde")
                return 'Producto No Corresponde'
            elif status == 4 and sc == 'Recogido Parcial':
                print("Substatus Homologation : Recogido Parcial")
                return 'Recogido Parcial'
            else: 
                print("Not substatus code to homologate or not homologation for the substatus code'")
