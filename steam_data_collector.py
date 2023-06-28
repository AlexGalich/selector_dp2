import requests 
from bs4 import BeautifulSoup
import re
import requests

from urllib import parse 

import numpy as np
import statistics
import time

import datetime

class Steam():

    

        # finds id of the product
    def get_id(self,s):
        id = None
        for script in s.find_all('script'):
            id_regex = re.search('Market_LoadOrderSpread\(([ 0-9]+)\)', script.text)
            if id_regex:
                id = id_regex.groups()[0].strip()
                break
        return id

    def get_order_price(self, item_name):
        time.sleep(7)
        name_encoded = parse.quote(item_name)
        name_url = f"https://steamcommunity.com/market/listings/730/{name_encoded}"
        html = requests.get(name_url).text
        time_increment = 30
        while html == None:
            time.sleep(time_increment)
            html = requests.get(name_url).text
            time_increment + 15

        soup = BeautifulSoup(html, 'lxml')
        id = self.get_id(soup)

        if id:
            id_url = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={id}&two_factor=0"
            time.sleep(10)
            html = requests.get(id_url).json()
            time_increment = 30

            while html == None:
                time.sleep(time_increment)
                html = requests.get(id_url).json()
                time_increment + 15

            soup = BeautifulSoup(html['buy_order_summary'], 'lxml')

            not_format = soup.select_one('span:last-child').text
            formated_price = float(not_format[1:])
            return formated_price

        else:
            print("Could not get ID")
            exit()

    

    # a function to extract a list of first 10 sellers offers

    def get_selling_price(self, item_name):
        name_encoded = parse.quote(item_name)
        try:
            current_sale_price = requests.get(f'https://www.csgostocks.de/api/prices/price/keyfigures/{name_encoded}').json()['steam']['current_price']
        except: 
            print("There is no selling price for", item_name)
            current_sale_price = None
        return current_sale_price

    def get_avg_month(self, item_name):
        name_encoded = parse.quote(item_name)
        dates_sum = {}
        dates_count = {}
        return_obj = requests.get(f'https://www.csgostocks.de/api/prices/price/{name_encoded}?name={name_encoded}').json()['data'][-720:]
        for i in return_obj[::-1]:
            date_only = str(datetime.datetime.fromtimestamp(i[0])).split(' ')[0]
        
            dates_sum[date_only] = dates_sum.get(date_only,0) +  float(i[1])
            dates_count[date_only] = dates_count.get(date_only, 0) + 1
            if len(dates_sum) >= 10:
                        break
        date_list = []

        for key in dates_sum:
        
            day_avg  = round(dates_sum[key]/ dates_count[key],2)
            date_list.append(day_avg)
       

        
        return  date_list[::-1]

    def calculate_grpath_sign(self, data):


        x = np.arange(len(data))  # Generate x values as indices (0, 1, 2, ...)
        slope = np.polyfit(x, data, 1)[0]
        mean_value = statistics.mean(data) 
        slope_mean_ratio = slope / mean_value

        std_mean_ration = statistics.stdev(data) / mean_value

        return slope_mean_ratio,std_mean_ration
        

    def calculate_steam_signal(self, selling_price, item_name):
       
       
       
        offer_price = self.get_selling_price(item_name)
        if offer_price == None:
            return False


        if selling_price <= (offer_price - (offer_price * 0.1)):
            
            
            mean_list  = self.get_avg_month(item_name)
            slope_mean_ratio,std_mean_ration = self.calculate_grpath_sign(mean_list)

            if slope_mean_ratio >= -0.008 :
                if std_mean_ration <= 0.06:
                    return True 
            
        return False 

        









