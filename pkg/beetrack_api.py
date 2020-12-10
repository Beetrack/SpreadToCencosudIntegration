import requests, json, os

class BeetrackAPI():

    def __init__(self, api_key):
        # En caso de que pase a ser bidireccional cambiar la api key por un parametro a entregar.
        #self.base_url = "https://app.beetrack.com/api/external/v1"
        self.api_key = api_key
        self.headers = { "Content-Type" : "application/json","X-AUTH-TOKEN": self.api_key}

    def base_url_for_account(self, account_id):
        if account_id == os.environ.get("account_id_paris"):
            base_url = "https://app.beetrack.dev/api/external/v1"
            return base_url
        else:
            base_url = "https://app.beetrack.com/api/external/v1"
            return base_url

    def create_route(self, payload, account_id):
        url = self.base_url_for_account(account_id)+"/routes"
        r = requests.post(url, json = payload, headers = self.headers).json()
        return r

    def get_route(self, id, account_id):
        url = self.base_url_for_account(account_id)+ "/routes/" + str(id)
        r = requests.get(url, headers = self.headers).json()
        return r

    def update_route(self, id, payload, account_id):
        url = self.base_url_for_account(account_id)+"/routes/" + str(id)
        r = requests.put(url, json = payload, headers = self.headers).json()
        return r

    def create_truck(self, payload, account_id):
        url = self.base_url_for_account(account_id)+"/trucks"
        r = requests.post(url, json = payload, headers = self.headers).json()
        return r

    def get_trucks(self, account_id):
        url = self.base_url_for_account(account_id)+"/trucks"
        r = requests.get(url, headers = self.headers).json()
        return r

    def update_dispatch(self, id, payload, account_id):
        url = self.base_url_for_account(account_id)+"/dispatches/" + str(id)
        r = requests.put(url, json = payload, headers = self.headers).json()
        return r

    def filter_dispatch(self, tag, route_id, account_id):
        url = self.base_url_for_account(account_id)+"/dispatches?cf[{}]={}&rd=5".format(tag,route_id)
        r = requests.get(url, headers = self.headers).json()
        return r 
