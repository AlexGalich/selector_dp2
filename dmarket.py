import requests 
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib import parse
from nacl.bindings import crypto_sign
from furl import furl




# change url to prod
rootApiUrl = "https://api.dmarket.com"


# change url to prod
rootApiUrl = "https://api.dmarket.com"

public_key = '3da7a04c31f0a5305370ee0dd2fa51a6cd338268efa687c1f424784a8d829723'
secret_key = 'dfe8772a7374397c00dab6e5e3ad37939ba71f64ac1889a905c95df5ff6cd62f3da7a04c31f0a5305370ee0dd2fa51a6cd338268efa687c1f424784a8d829723'
API_URL ="https://api.dmarket.com"
# Create a function to encode item to a link


def generate_headers(method, api_path, body: dict = None):
        
        # replace with your api keys
        public_key = "3da7a04c31f0a5305370ee0dd2fa51a6cd338268efa687c1f424784a8d829723"
        secret_key = "dfe8772a7374397c00dab6e5e3ad37939ba71f64ac1889a905c95df5ff6cd62f3da7a04c31f0a5305370ee0dd2fa51a6cd338268efa687c1f424784a8d829723"

        

        nonce = str(round(datetime.now().timestamp()))
        string_to_sign = method + api_path
    
        if body != None:
            string_to_sign += json.dumps(body)
        string_to_sign += nonce
        signature_prefix = "dmar ed25519 "
        encoded = string_to_sign.encode('utf-8')
        
        signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
        signature = signature_bytes[:64].hex()
        headers = {
            "X-Api-Key": public_key,
            "X-Request-Sign": signature_prefix + signature,
            "X-Sign-Date": nonce
        }
        return headers




def encode_item(item_name):
    new_string = parse.quote(item_name)

    return new_string


# Get the balance in the usd cents (1 dollar = 100)
def get_balance():
    method = 'GET'
    url_path ='/account/v1/balance'
    header = generate_headers(method, url_path)
    url = API_URL + url_path
    market_response = requests.get(url,headers=header)
    try:
        balance = json.loads(market_response.text)['usd']
    except:
        return None
    return balance



def get_invetory_items():
    method = 'GET'
    url_path ='/marketplace-api/v1/user-inventory?GameID=a8db&BasicFilters.InMarket=true'
    header = generate_headers(method, url_path)
    market_response = requests.get(API_URL + url_path ,headers=header)
   
    inventory = json.loads(market_response.text)["Items"]
    


    return inventory

def get_available_inventory(items):

    return_items_list = []
    for item in items :
            item_info = {'ItemID': item['AssetID'],
                        'ItemName': item['Title'],
                        'InstantPrice': item['InstantPrice']['Amount'],
                        }
            
            return_items_list.append(item_info) 

    return return_items_list


 


def get_market_value():
    method = 'GET'
    url_path ='/exchange/v1/user/items'
    params = {'gameId' : 'a8db', 'currency' :'USD'}
    header = generate_headers(method, url_path,params)
    market_response = requests.get('https://api.dmarket.com/exchange/v1/market/items?gameId=a8db&limit=100&offset=0&orderBy=title&orderDir=desc&currency=USD&priceFrom=0&priceTo=0',headers=header)
  
    market_sale = json.loads(market_response.text)['objects']

    item_prices = 0
    
    for item in market_sale[:2]:
        
        
        item_prices += int(item['price']['USD'])

    return item_prices 

def get_selling_items():
    header = method = 'GET'
    url_path ='/exchange/v1/user/offers?side=user&orderBy=updated&orderDir=desc&title=&priceFrom=0&priceTo=0&treeFilters=&gameId=a8db&cursor=&limit=100&currency=USD'
    header = generate_headers(method, url_path)
    market_response = requests.get(API_URL + url_path ,headers=header)
    
    selling_items = json.loads(market_response.text)['objects']
    return selling_items
    
    

def put_on_sale(item_id, price):
    header = method = 'POST'
    url_path ='/marketplace-api/v1/user-offers/create'
    
    data = {
        "Offers": [
            {
            "AssetID": item_id,
            "Price": {
                "Currency": "USD",
                "Amount": price
            }
            }
        ]
        }
    
    header = generate_headers(method, url_path, body=data)
    response = requests.post(API_URL + url_path ,headers=header, json = data)

    return response.json()

def remove_item_from_sale(item_id, offer_id , price):
    method = "DELETE"
    url_path ='/exchange/v1/offers'
    
    data = {
        "force": True,
        "objects": [
            {
            "itemId": item_id,
            "offerId": offer_id,
            "price": {
                "amount": price,
                "currency": "USD"
            }
            }
        ]
        }
        
    header = generate_headers(method, url_path, body=data)

    response = requests.delete(API_URL + url_path ,headers=header, json = data)
    return response.json()

def update_sale_price(item_id, offer_id , price):
    method = "POST"
    url_path = "/marketplace-api/v1/user-offers/edit"
    data ={
        "Offers": [
            {
            "OfferID": offer_id,
            "AssetID": item_id,
            "Price": {
                "Currency": "USD",
                "Amount": price
            }
            }
        ]
        }
    
    header = generate_headers(method, url_path, body=data)
    response = requests.post(API_URL + url_path ,headers=header, json = data)
    

    return response.json()



def place_target(item_name,order_amount, order_price):
    method = "POST"
    url_path = "/marketplace-api/v1/user-targets/create"
    
    data = {
        "GameID": "a8db",
        "Targets": [
            {
            "Amount": order_amount,
            "Price": {
                "Currency": "USD",
                "Amount": order_price
            },
            "Title": item_name
            }
        ]
        }
    
    header = generate_headers(method, url_path, body=data)
    response = requests.post(API_URL + url_path ,headers=header, json = data)

    return response.json()

def remove_target(target_id):
    method = "POST"
    url_path = "/marketplace-api/v1/user-targets/delete"
    
    data = {
        "Targets": [
            {
            "TargetID": target_id
            }
        ]
        }
    
    header = generate_headers(method, url_path, body=data)
    response = requests.post(API_URL + url_path ,headers=header, json = data)
   

    return response.json()

def construct_dict(items_list):
    dictionary = {}

    for item in items_list:
        target_price = float(item['InstantPrice']) /100
        item_id = item['ItemID']

        if dictionary.get(item['ItemName'], False):

            if dictionary[item['ItemName']]['highest_target'] < target_price :
                dictionary[item['ItemName']]['highest_target'] = target_price
            dictionary[item['ItemName']]['item_ids'].append(item_id)
            

        else :
            schema = {'highest_target': target_price,
                        'item_ids' : [item_id]}
            

            dictionary[item['ItemName']] = schema
    return dictionary


def get_item_id(item):
    item_id = item['itemId']
    return item_id

def get_offer_id(item):
    offer_id  = item['extra']['offerId']
    return offer_id

def get_item_name(item):
    item_name = item['title']
    return item_name



def get_closed_offers():
    method = 'GET'
    url_path = "/marketplace-api/v1/user-offers/closed"
    header = generate_headers(method, url_path)
    market_response = requests.get(API_URL + url_path ,headers=header)
    
   
    
    return market_response.json()['Trades']


def balance_evaluation(item_price, item_quanity):
    balance_cents = int(get_balance())
    balance  = balance_cents / 100

    if (item_price * item_quanity) < balance :
        return True 
    else :
        return False 
    
def get_sales_history(item_name):
    item_encoded = encode_item(item_name)
    method = "GET"
    url_path = f'/marketplace-api/v1/sales-history?Title={item_encoded}&GameID=a8db&Period=7D&Currency=USD'
    header = generate_headers(method, url_path)
    market_response = requests.get(API_URL + url_path ,headers=header)

    try:
        hist = json.loads(market_response.text)
      
        return hist['SalesHistory']
    
    except:
        return None




#print('===================================================')
#print(put_on_sale('b7ecd156-8eee-5427-9d5d-67671aa426cd',0.87))
#{'Result': [{'CreateOffer': {'AssetID': 'b7ecd156-8eee-5427-9d5d-67671aa426cd', 'Price': {'Currency': 'USD', 'Amount': 0.87}}, 'OfferID': '98dec468-d245-481d-b4c5-70749bbffd6c', 'Successful': True, 'Error': None}]}
#print(remove_target('6ab1c715-894c-41fe-8d7b-a097ad29d945'))
#place_target()
#invetory = len(get_invetory_items())
#print(invetory)
#print(get_closed_offers()[:5])
#avb_inv = get_available_inventory(invetory)
#invetory_dictionary = construct_dict(avb_inv)

#print(remove_item_from_sale('e48d211f-9282-59e9-a254-afd54deb79be','ba8b62ef-3df6-4b3a-aa94-4e5a94b7fec6','41' ))
#(put_on_sale('e48d211f-9282-59e9-a254-afd54deb79be',0.41))

#print(update_sale_price('f708cbfc-b0a5-5050-bdfb-bd2fa3b98155','475121ba-7cce-44a7-b9f7-fa44dc91c001', 1.1 ))



