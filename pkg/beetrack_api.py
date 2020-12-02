import requests, json

class BeetrackAPI():

    def __init__(self, api_key):
        # En caso de que pase a ser bidireccional cambiar la api key por un parametro a entregar.
        self.base_url = "https://app.beetrack.com/api/external/v1"
        self.api_key = api_key
        self.headers = { "Content-Type" : "application/json","X-AUTH-TOKEN": self.api_key}

    def create_route(self, payload):
        url = self.base_url+"/routes"
        r = requests.post(url, json = payload, headers = self.headers).json()
        return r

    def get_route(self, id):
        print(id)
        print(self.api_key)
        url = self.base_url+ "/routes/" + str(id)
        r = requests.get(url, headers = self.headers).json()
        return r

    def update_route(self, id, payload):
        url = self.base_url+"/routes/" + str(id)
        r = requests.put(url, json = payload, headers = self.headers).json()
        return r

    def create_truck(self, payload):
        url = self.base_url+"/trucks"
        r = requests.post(url, json = payload, headers = self.headers).json()
        return r

    def get_trucks(self):
        url = self.base_url+"/trucks"
        r = requests.get(url, headers = self.headers).json()
        return r

    def update_dispatch(self, id, payload):
        url = self.base_url+"/dispatches/" + str(id)
        r = requests.put(url, json = payload, headers = self.headers).json()
        return r

    def filter_dispatch(self, tag, route_id):
        url = self.base_url+"/dispatches?cf[{}]={}&rd=5".format(tag,route_id)
        r = requests.get(url, headers = self.headers).json()
        return r 
