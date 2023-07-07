import pandas as pd

import schedule
import time

from item_tracker import ItemTracker
from data_writer import  DataWriter
from helper_functions import collect_item_data, check_appeared_in_sales_history, extract_sales_history, match_disappeared_ids
from hidden import API_URL, public_key, secret_key, hostname, database, username, port, col_names

def collect_items(item_tracker, current_ids, data_writer, table_name, original_offer_ids, list_of_item_names, params, periodicity):
    # Make a copy of paramaters
    params_copy = params.copy()

    # Retrieve updated items
    item_tracker.track_items(list_of_item_names, params_copy)
    new_items = item_tracker.get_items()

    # Iterate over new items and insert into the database if offer ID is unique
    for item in new_items.itertuples(index=False):
        series_item = pd.Series(item, index=new_items.columns)
        offer_id = series_item["extra.offerId"]

        # If the item is NOT unique, continue
        if (offer_id in original_offer_ids) or (offer_id in current_ids):
            continue

        else:
            current_ids.append(offer_id)
            series_item = series_item.replace('', None)

            # Collect item data  
            data = collect_item_data(series_item, periodicity)
            # Save data to database
            data_writer.write_item_data(data, table_name)

            disappeared_ids = [offer_id for offer_id in current_ids if offer_id not in new_items["extra.offerId"].values]
            sales_history = extract_sales_history(series_item["title"])
            appeared_in_sales_history = check_appeared_in_sales_history(sales_history, periodicity)

            print()
            print(disappeared_ids, appeared_in_sales_history)
            print()

            if appeared_in_sales_history and len(disappeared_ids) > 0:
                matched_data = match_disappeared_ids(disappeared_ids, sales_history)
                data_writer.append_sales_info(disappeared_ids, matched_data, table_name)
            
            else:
                disappeared_ids.clear()

            
# TODO: add all arguments inside the job function
def job(data_writer, current_ids, table_name, original_offer_ids, list_of_item_names, params, periodicity):
    print("Running the job...")

    item_tracker = ItemTracker(API_URL, public_key, secret_key)
    collect_items(item_tracker, current_ids, data_writer, table_name, original_offer_ids, list_of_item_names, params, periodicity)

def main():
    params = {
        "gameId": "a8db",
        "currency": "USD",
        "limit": 100,
        "priceFrom": 0,
        "priceTo": 400,
        "orderBy": "price",
        "orderDir": "asc",
    }   
    # titles = ["StatTrak™ P250 | Red Rock (Field-Tested)", "Souvenir P250 | Gunsmoke (Minimal Wear)", "Nova | Green Apple (Field-Tested)", "Snakebite Case"]
    titles = ["Snakebite Case"]

    original_item_tracker = ItemTracker(API_URL, public_key, secret_key)
    original_item_tracker.track_items(titles, params)
    original_items = original_item_tracker.get_items()
    original_offer_ids = original_item_tracker.get_history_offer_ids()

    # # Create a new item tracker
    # item_tracker = ItemTracker(API_URL, public_key, secret_key)

    # Initialize an item data writer
    table_name = "items" # <-- Table name
    item_data_writer = DataWriter(hostname, database, username, port, col_names, table_name)
    current_ids = []

    # Schedule the job to run every 5 minutes
    schedule.every(10).seconds.do(job, item_data_writer, current_ids, table_name, original_offer_ids, titles, params, 1)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()