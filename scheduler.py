from apscheduler.schedulers.background import BackgroundScheduler
from data_manager import DataManager
from ebay_client import EbayClient
from datetime import datetime
import time
import atexit

class LegendastiqueScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.data_manager = DataManager()
        self.ebay_client = EbayClient()

    def start(self):
        # Run check_prices every 24 hours
        self.scheduler.add_job(func=self.check_prices, trigger="interval", hours=24)
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())

    def check_prices(self):
        self.check_prices_manual()

    def check_prices_manual(self):
        print(f"[{datetime.now()}] Starting automated price check...")
        
        # Reload to ensure we have items added via API since startup
        self.data_manager.reload_data()
        
        items = self.data_manager.get_items()
        results = []
        
        for item in items:
            result = self._check_single_item_logic(item)
            results.append(result)
        
        print(f"[{datetime.now()}] Price check completed.")
        return results

    def check_item_by_id(self, item_id):
        """Checks price for a single item by ID"""
        self.data_manager.reload_data()
        items = self.data_manager.get_items()
        item = next((i for i in items if i['id'] == item_id), None)
        
        if item:
            print(f"[{datetime.now()}] Checking single item: {item.get('name')}")
            return self._check_single_item_logic(item)
        return {"error": "Item not found"}

    def _check_single_item_logic(self, item):
        name = item.get('name')
        try:
            # Get the LOWEST MARKET price (excluding own listings)
            exclude_keywords = item.get('excludeKeywords', [])
            # Support both list and comma-separated string (just in case)
            if isinstance(exclude_keywords, str):
                exclude_keywords = exclude_keywords.split(',')
                
            price, date_str, url = self.ebay_client.get_lowest_market_price(name, exclude_keywords)
            
            if price:
                print(f"  Market Price: £{price}")
                self.data_manager.add_history_point(item['id'], date_str, price, url)
                return {"id": item['id'], "name": name, "price": price, "url": url, "status": "success"}
            else:
                print(f"  No market listings found for {name}")
                return {"id": item['id'], "name": name, "status": "no_listings"}
        except Exception as e:
            print(f"  Error checking {name}: {e}")
            return {"id": item['id'], "name": name, "status": "error", "message": str(e)}

scheduler = LegendastiqueScheduler()
