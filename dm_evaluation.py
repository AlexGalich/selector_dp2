import requests
from bs4 import BeautifulSoup
from dmarket_info import encode_item
import csv 
import json
import time


def request_sales_history(item_encoded):
    header = {'authorization': 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyMTJlMDEzMC03ZjQ4LTQwNGMtODE5NC1jMWViMTBmZDZlM2YiLCJleHAiOjE2ODg0MDcyNTIsImlhdCI6MTY4NTgxNTI1Miwic2lkIjoiMDk4ODkwZjctNjI1OC00ZTcxLWJkY2ItZTQ4Y2Y4MmE1ZGZhIiwidHlwIjoiYWNjZXNzIiwiaWQiOiIxNjViMWE3Yy1kZDZmLTQ0YzYtYjI2MC02OGU1NTA4OTFiMTAiLCJwdmQiOiJtcCIsInBydCI6IjIzMDYiLCJhdHRyaWJ1dGVzIjp7IndhbGxldF9pZCI6Ijc2YWYwMjU5MmMzZGRmZDFkNGFlOTZmYmQ1NmM4ZGJmOWVmOGZlNTUwMjZlZGJlMjg4MzBiMmE3ZTcxOTRkZTMiLCJzYWdhX3dhbGxldF9hZGRyZXNzIjoiMHgxMDBmM2UwZDBkRDRhQjE3NDJmRWVGMjA3NzcwNEU3MjM0YzVmYmRjIiwiYWNjb3VudF9pZCI6IjM2YzljOTEzLWQwYWQtNGRjYy05NDUzLTEyNGIyZjE0OGU5OSJ9fQ.Sh3wEQxX_oCyV9XEbViyTRWF3a-NoEsZDh-TgIpwe2e3T1jnva2zurjQdHNJJV1jJrhI0ipVGk0fx-m3zhVZLQ'}
    market_response = requests.get(f'https://api.dmarket.com/marketplace-api/v1/sales-history?Title={item_encoded}&GameID=a8db&Period=7D&Currency=USD',headers=header)
    try:
        print(market_response.status_code)
        hist = json.loads(market_response.text)

        return hist['SalesHistory']
    
    except:
        return None
    

def check_amount_criterias(item_info):
    if item_info == None:
        return False 
    
    else:
        higher_15 = all(i >= 5 for i in item_info['Items'][:-1])
      
        if higher_15 :
            return True 
        else :
            return False
def check_price_criteria(item_info):
    # Get sale price in cents , convert them from str to int
    
    if item_info == None:
        return False 
    
    price_list = item_info['Prices']
    if '' in price_list:
        return False


    item_prices = [eval(i) for i in item_info['Prices']] 
    if len(item_prices) == 0:
        return False
   
    avg_prices = sum(item_prices)/ len(item_prices)
   
        

    if avg_prices < 1100 and avg_prices >= 20:
         
            return True 
    return False 

       

 
 

def calculate_dm_signal(item_name):


    encoded_item = encode_item(item_name)
    
    item_infos = request_sales_history(encoded_item)
    amount_criteria = check_amount_criterias(item_infos)
    price_criteria = check_price_criteria(item_infos)
    

    if amount_criteria and price_criteria :
        return True 
    return  False




