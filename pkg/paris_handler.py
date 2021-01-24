import os
from .beetrack_api import BeetrackAPI
from .commons import ignore_none_value, fetch_tag_value

class ParisHandler():

    def __init__(self, body):
        self.body = body
        self.api_key = os.environ.get('paris_api_key')
        self.base_url = 'https://app.beetrack.dev/api/external/v1'
        BeetrackAPI.__init__(self, self.api_key, self.base_url)

    def update_dispatch(self):
        self.body.pop('resource')
        self.body.pop('event')
        self.body.pop('account_name')
        self.body.pop('account_id')
        guide = self.body.get('guide')
        self.body.pop('guide')
        self.body.pop('identifier')
        self.body.pop('route_id')
        self.body.pop('truck_identifier')
        self.body.pop('contact_identifier')
        self.body.pop('substatus')
        substatus = self.homologate_substatus()
        self.body.update({'substatus_code' : substatus})
        items = self.body.get('items')
        for item in items:
            item.pop('id')
            item.pop('extras')
        self.body.update({'destination' : None})
        self.body.update({'place' : None})
        tags = self.body.get('tags')
        id_dispatch_paris = fetch_tag_value(tags, 'id_dispatch_paris')
        self.body.update({'dispatch_id' : int(id_dispatch_paris)})
        payload = self.body
        print({"Update Dispatch Status Payload": payload})
        create = BeetrackAPI(self.api_key, self.base_url).update_dispatch(guide, payload)
        print({"Beetrack Response" : create},{"Payload to update" : payload})
        return create

    def update_trunk_dispatch(self):
        status = self.body.get('status')
        guide = self.body.get('guide')
        guide_on_paris = guide.replace('PAR-', '')
        tags = self.body.get('tags')
        id_dispatch_paris = fetch_tag_value(tags, 'id_dispatch_paris')
        payload = {
            'status' : int(status),
            'place':  'CT Spread',
            'dispatch_id' : int(id_dispatch_paris)
        }
        print({"Request payload" : payload})
        update = BeetrackAPI(self.api_key, self.base_url).update_dispatch(guide_on_paris, payload)
        return update

    def homologate_substatus(self):
        status = self.body.get('status')
        substatus_code = self.body.get('substatus')
        sc = substatus_code
        if sc == None:
            print("Not substatus code to homologate or not homologation for the substatus code")
            return True
        else:
            if status == 2 and sc == 'Entrega exitosa':
                print("Substatus Homologation : En Cliente")
                return '61'
            elif status == 3 and sc == 'Sin Moradores':
                print("Substatus Homologation : Cliente No Está")
                return '03'
            elif status == 3 and sc == 'No se encuentra direccion':
                print("Substatus Homologation : Dirección Errónea")
                return '02'
            elif status == 3 and (sc == 'Dificultad para llegar a domicilio' or sc == 'Recibe en segunda visita' or sc == 'Otro tipo de problema (describir)' or sc == 'Fuera de Rango' or sc == 'No se encuentra direccion'):
                print('Substatus Homologation : Motivos Transporte')
                return '06'
            elif status == 3 and sc == 'Domicilio no corresponde':
                print("Substatus Homologation : Motivos Cliente")
                return '30'
            elif status == 3 and sc == 'Anulará, incompleto o cambiado':
                print("Substatus Homologation : Expectativa")
                return '51'
            elif status == 3 and sc == 'Producto dañado':
                print("Substatus Homologation : Daño Producto")
                return '52'
            elif status == 3 and sc == 'Producto No Corresponde':
                print("Substatus Homologation : Producto No Corresponde")
                return '53'
            elif status == 3 and sc == 'Dirección Errónea - Definitivo':
                print("Substatus Homologation : Dirección Errónea - Definitivo")
                return '92'
            elif status == 3 and sc == 'Cliente No Está - Definitivo':
                print("Substatus Homologation : Cliente No Está - Definitivo")
                return '93'
            elif status == 3 and sc == 'Motivos Cliente - Definitivo':
                print("Substatus Homologation : Motivos Cliente - Definitivo")
                return '930'
            elif status == 3 and (sc == 'Motivos Transporte - Definitivo' or sc == 'Robado' or sc == 'Extraviado'):
                print("Substatus Homologation : Motivos Transporte - Definitivo")
                return '96'
            elif status == 3 and sc == 'Nota de Crédito':
                print("Substatus Homologation : Nota de Crédito")
                return '55'
            elif status == 3 and sc == 'Error sistémico':
                print("Substatus Homologation : Error sistémico")
                return '31'
            elif status == 4 and sc == 'Expectativa':
                print("Substatus Homologation : Expectativa")
                return '51'
            elif status == 4 and sc == 'Daño Producto':
                print("Substatus Homologation : Daño Producto")
                return '52'
            elif status == 4 and sc == 'Producto No Corresponde':
                print("Substatus Homologation : Producto No Corresponde")
                return '53'
            else: 
                print("Not substatus code to homologate or not homologation for the substatus code'")
