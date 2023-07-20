public_key = '3da7a04c31f0a5305370ee0dd2fa51a6cd338268efa687c1f424784a8d829723'
secret_key = 'dfe8772a7374397c00dab6e5e3ad37939ba71f64ac1889a905c95df5ff6cd62f3da7a04c31f0a5305370ee0dd2fa51a6cd338268efa687c1f424784a8d829723'
API_URL = "https://api.dmarket.com"

hostname="localhost"
database="DmarketTradingDB"
username="andriievskyi"
port=5432

col_names = {
    'offer_id': 'VARCHAR',
    'title': 'VARCHAR',
    'created_at': 'TIMESTAMP',
    'price_usd': 'NUMERIC',
    'instance_price_usd': 'NUMERIC',
    'exchange_price_usd': 'NUMERIC',
    'recommended_price_offer_price_usd': 'NUMERIC',
    'recommended_price_d3_usd': 'NUMERIC',
    'recommended_price_d7_usd': 'NUMERIC',
    'recommended_price_d7_plus_usd': 'NUMERIC',
    'is_new': 'BOOLEAN',
    'quality': 'VARCHAR',
    'category': 'VARCHAR',
    'trade_lock_duration': 'VARCHAR',
    'item_type': 'VARCHAR',
    'collection': 'VARCHAR',
    'delivery_stats_rate': 'NUMERIC',
    'discount_price_usd': 'NUMERIC',
    'sale_price_usd': 'NUMERIC',
    'sale_datetime': 'TIMESTAMP'
    # 'trade_lock': 'BOOLEAN'
}
