import psycopg2

class DataWriter():
    def __init__(self, hostname:str, database:str, username:str, port:int, col_names:dict=None, table_name:str=None):
        self._hostname = hostname
        self._database = database
        self._username = username
        self._port = port  

        try:
            # Connect to the PostgreSQL server and create a cursor object for executing queries
            print("Connecting...")
            self._connect_to_db()
        except:
            raise Exception('Failed connecting to DB')
        
        else:
            if col_names is not None and table_name is not None:
                self._create_table(col_names, table_name)
            elif col_names is not None or table_name is not None:
                raise ValueError("Both 'col_names' and 'table_name' must be provided or left as None.")

        

    def write_item_data(self, data: dict, table_name: str):
        if not data:
            return  # If data is empty, no need to proceed

        keys = data.keys()

        # Generate the placeholder strings for the SQL query
        placeholders = ', '.join(['%s'] * len(keys))

        # Generate the INSERT query
        query = f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({placeholders})"

        # Extract the values from the data dictionary and execute the INSERT query
        values = list(data.values())
        self._cur.execute(query, values)

        self._conn.commit()

    def append_sale_info(self, disappeared_ids, data, table_name):
        ids_copy = disappeared_ids.copy()

        for item_id in ids_copy:
            price = data[item_id]['Price']
            time = data[item_id]['Time']
            # Add code to append the price and time to the database
            query = f"INSERT INTO {table_name} (sale_price_usd, sale_datetime) VALUES (?, ?)"
            values = (price, time)
            self._cur.execute(query, values)
            self._conn.commit()

            disappeared_ids.remove(item_id)
            print(f"Appending sale info: Price={price}, Time={time}")

    def _connect_to_db(self):
        self._conn = psycopg2.connect(
            host=self._hostname,
            dbname=self._database,
            user=self._username,
            port=self._port
        )

        self._cur = self._conn.cursor()

    def _create_table(self, col_names:dict, table_name: str):
        query = f"CREATE TABLE IF NOT EXISTS  {table_name} ("

        for col_name, data_type in col_names.items():
            query += f"{col_name} {data_type}, "

        query = query.rstrip(", ")  # Remove the trailing comma and space
        query += ")"

        self._cur.execute(query)
        self._conn.commit()


    def _close_connection(self):
        self._conn.close()