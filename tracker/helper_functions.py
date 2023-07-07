import pandas as pd
import psycopg2
import datetime

import statistics
import requests
import json

from hidden import hostname, database, username, port

def get_avg_time(minute_difference:int=20):
    now = datetime.datetime.now()
    n_minutes_ago = now - datetime.timedelta(minutes=minute_difference)
    
    # Convert datetime objects to timestamps
    now_timestamp = now.timestamp()
    n_minutes_ago_timestamp = n_minutes_ago.timestamp()
    
    # Calculate the average timestamp
    avg_timestamp = (now_timestamp + n_minutes_ago_timestamp) / 2
    
    # Convert the average timestamp back to a datetime object
    created_at = datetime.datetime.fromtimestamp(avg_timestamp)
    return created_at

def connect_to_db():
    conn = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        port=port
    )

    cur = conn.cursor()

    return conn, cur

def collect_item_data(item, periodicity) -> dict:
    data = {
        'offer_id': item['extra.offerId'],
        "title": item["title"],
        'created_at': get_avg_time(minute_difference=periodicity),
        'price_usd': float(item['price.USD']) if item['price.USD'] is not None else None,
        'instance_price_usd': float(item['instantPrice.USD']) if item['instantPrice.USD'] is not None else None,
        'exchange_price_usd': float(item['exchangePrice.USD']) if item['exchangePrice.USD'] is not None else None,
        'recommended_price_offer_price_usd': float(item['recommendedPrice.offerPrice.USD']) if item['recommendedPrice.offerPrice.USD'] is not None else None,
        'recommended_price_d3_usd': float(item['recommendedPrice.d3.USD']) if item['recommendedPrice.d3.USD'] is not None else None,
        'recommended_price_d7_usd': float(item['recommendedPrice.d7.USD']) if item['recommendedPrice.d7.USD'] is not None else None,
        'recommended_price_d7_plus_usd': float(item['recommendedPrice.d7Plus.USD']) if item['recommendedPrice.d7Plus.USD'] is not None else None,
        'is_new': item['extra.isNew'],
        'quality': item['extra.quality'],
        'category': item['extra.category'],
        'trade_lock_duration': item['extra.tradeLockDuration'],
        'item_type': item['extra.itemType'],
        'collection': item['extra.collection'],
        'delivery_stats_rate': item['deliveryStats.rate'],
        'discount_price_usd': float(item['discountPrice.USD']) if item['discountPrice.USD'] is not None else None
    }

    return data

# TODO
# FIX HERE
def check_appeared_in_sales_history(sales_history, interval_minutes):
    current_time = datetime.datetime.now()
    interval_start = current_time - datetime.timedelta(minutes=interval_minutes)
    
    for sale in sales_history:
        sale_time = datetime.datetime.fromtimestamp(int(sale['Date']))
        if interval_start <= sale_time <= current_time:
            return True
    
    return False

def extract_sales_history(item):
    market_response = requests.get(f'https://api.dmarket.com/marketplace-api/v1/last-sales?Title={item}&GameID=a8db&Currency=USD')
    
    print(market_response.text)
    sales = json.loads(market_response.text)['LastSales']

    return sales

def calculate_seconds(date_from, date_to):
   
    time_difference = date_to - date_from 
    days_sale = time_difference.days * 86400
    second_sale = time_difference.seconds
    time_difference_seconds = days_sale+ second_sale
 
    return round((time_difference_seconds / 3600) , 2)

# TODO
# FIX HERE
def extract_sales_information(item):
    sales_info = extract_sales_history(item)

    if sales_info != None:
        return_obj = {'total_count': len(sales_info)}

        Date = []
        Price = []
        last_record = None
        time_diff = []
        last_20_sales = []
        for sale in sales_info:

            Date.append(int(sale['Date']))
            Price.append(int(sale['Price']['Amount']))

            if len(last_20_sales) < 20:
                last_20_sales.append(int(sale['Price']['Amount'])/100)
            
            if last_record == None :
                last_record = datetime.datetime.fromtimestamp(int(sale['Date']))
               
            else: 
                new_record = datetime.datetime.fromtimestamp(int(sale['Date']))
                time_diff.append(calculate_seconds(new_record ,last_record))
                last_record = datetime.datetime.fromtimestamp(int(sale['Date']))
        try:
            return_obj['min_price'] = min(Price) /100
        except:
            return_obj['min_price'] = 0
        try:
            return_obj['max_price'] = max(Price)/100
        except :
            return_obj['max_price'] = 0 
        return_obj['mean_price'] = statistics.mean(Price) / 100
        return_obj['mode_price'] = statistics.mode(Price)/ 100
        return_obj['last_sale'] = calculate_seconds( datetime.datetime.fromtimestamp(int(sales_info[0]['Date'])), datetime.now())
        return_obj['avg_sale_time'] = statistics.mean(time_diff) 
        return_obj['last_10_sales'] = last_20_sales

        return return_obj
    return None

def match_disappeared_ids(disappeared_ids, sales_history):
    matched_data = {}

    for disappeared_id in disappeared_ids:
        disappeared_price = None
        disappeared_time = None
        min_price_diff = float('inf')
        min_time_diff = float('inf')

        for sale in sales_history:
            sale_price = float(sale['Price']['Amount'])
            sale_time = datetime.datetime.fromtimestamp(int(sale['Date']))

            price_diff = abs(disappeared_price - sale_price)
            time_diff = abs(disappeared_time - sale_time)

            if price_diff < min_price_diff and time_diff < min_time_diff:
                disappeared_price = sale_price
                disappeared_time = sale_time
                min_price_diff = price_diff
                min_time_diff = time_diff

        matched_data[disappeared_id] = {
            'Price': disappeared_price,
            'Time': disappeared_time
        }

    return matched_data
