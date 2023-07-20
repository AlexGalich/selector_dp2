import pandas as pd
from nacl.bindings import crypto_sign
from datetime import datetime
import json
import requests

class ItemTracker:
    def __init__(self, API_URL, public_key, secret_key):
        self._API_URL = API_URL
        self._public_key = public_key
        self._secret_key = secret_key
        self._history_offer_ids = []
        self._items = pd.DataFrame()  

    def get_items(self):
        return self._items

    def get_history_offer_ids(self): 
        return self._history_offer_ids
    
    def get_api_items(self, params=None): 
        method = 'GET'
        url_path = '/exchange/v1/market/items'
        if params:
            url_path += "?" + "&".join([f"{key}={value}" for key, value in params.items()])

        header = self.generate_headers(method, url_path)
        url = self._API_URL + url_path

        market_response = requests.get(url, headers=header)

        try:
            items = json.loads(market_response.text)
            return items
        except Exception as e:
            return e
        
    # Track each item in the list of items
    def track_items(self, list_of_item_names: list, params: dict, price_offset: int = 50):
        updated_params = params.copy()
        max_price: int = updated_params["priceTo"]
        
        for item_name in list_of_item_names:
            go = True
            while go and updated_params["priceTo"] <= max_price:
                
                updated_params["title"] = item_name

                # Retrieve new items
                new_items = pd.json_normalize(self.get_api_items(updated_params)["objects"])

                if len(new_items) == 0:
                    go = False
                else:
                    # Extend the history list with the new item ids and add the item info to the dataframe
                    self._history_offer_ids.extend(new_items["extra.offerId"])
                    self._items = pd.concat([self._items, new_items], ignore_index=True)

                    # Offset the prices
                    current_top_price = self._items["price.USD"].astype(int).max()
                    updated_params["priceFrom"] = current_top_price + 1
                    updated_params["priceTo"] = current_top_price + 1 + price_offset

                print(f"Collected extra: {len(new_items)} items")
                print(f"Overall collected: {len(self._items)}")
                print(f"Overall unique items: {len(set(self._history_offer_ids))}")
                print(updated_params)


    def generate_headers(self, method, api_path, body=None):
        nonce = str(round(datetime.now().timestamp()))
        string_to_sign = method + api_path

        if body is not None:
            string_to_sign += json.dumps(body)
        string_to_sign += nonce
        signature_prefix = "dmar ed25519 "
        encoded = string_to_sign.encode('utf-8')

        signature_bytes = crypto_sign(encoded, bytes.fromhex(self._secret_key))
        signature = signature_bytes[:64].hex()
        headers = {
            "X-Api-Key": self._public_key,
            "X-Request-Sign": signature_prefix + signature,
            "X-Sign-Date": nonce
        }
        return headers

    def reset_items(self):
        self._items = pd.DataFrame()  
    
    def reset_history_offer_ids(self):
        self._history_offer_ids = []