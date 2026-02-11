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
            name = item.get('name')
            print(f"Checking price for: {name}...")
            
            # Get the LOWEST ACTIVE price (Market Floor)
            exclude_keywords = item.get('excludeKeywords', [])
            # Support both list and comma-separated string (just in case)
            if isinstance(exclude_keywords, str):
                exclude_keywords = exclude_keywords.split(',')
                
            price, date_str, url = self.ebay_client.get_lowest_price(name, exclude_keywords)
            
            if price:
                print(f"  Current active low: £{price}")
                self.data_manager.add_history_point(item['id'], date_str, price, url)
                results.append(f"✅ {name}: £{price}\n    Source: {url}")
            else:
                print(f"  No active listings found for {name}")
                results.append(f"❌ {name}: No active listings found")
        
        print(f"[{datetime.now()}] Price check completed.")
        return results

scheduler = LegendastiqueScheduler()
