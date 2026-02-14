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

    def _get_time_str(self):
        """Returns current time formatted for logs (UK Style: DD Mon HH:MM:SS)"""
        return datetime.now().strftime("%d %b %H:%M:%S")

    def check_prices(self):
        self.check_prices_manual()

    def check_prices_manual(self):
        print(f"[{self._get_time_str()}] Starting automated price check...")
        
        # Reload to ensure we have items added via API since startup
        self.data_manager.reload_data()
        
        items = self.data_manager.get_items()
        results = []
        
        for item in items:
            result = self._check_single_item_logic(item)
            results.append(result)
        
        print(f"[{self._get_time_str()}] Price check completed.")
        return results

    def check_item_by_id(self, item_id):
        """Checks price for a single item by ID"""
        self.data_manager.reload_data()
        items = self.data_manager.get_items()
        item = next((i for i in items if i['id'] == item_id), None)
        
        if item:
            print(f"[{self._get_time_str()}] Checking single item: {item.get('name')}")
            return self._check_single_item_logic(item)
        return {"error": "Item not found"}

    def _check_single_item_logic(self, item):
        name = item.get('name')
        try:
            # Get global exclusions
            settings = self.data_manager.get_settings()
            global_exclusions = settings.get("globalExclusions", "")
            
            # Get the LOWEST MARKET price (excluding own listings)
            exclude_keywords = item.get('excludeKeywords', [])
            # Support both list and comma-separated string (just in case)
            if isinstance(exclude_keywords, str):
                exclude_keywords = exclude_keywords.split(',') if exclude_keywords else []
            elif exclude_keywords is None:
                exclude_keywords = []

            # Combine user exclusions with globals? Or pass separately?
            # Passing separately allows clearer logic in ebay_client
            # Let's pass global_exclusions as a string or list
            
            price, date_str, url, confidence, rating = self.ebay_client.get_lowest_market_price(name, exclude_keywords, global_exclusions)
            
            if price:
                print(f"  Market Price: £{price} (Confidence: {rating} - {confidence}%)")
                self.data_manager.add_history_point(item['id'], date_str, price, url)
                
                # Save confidence to item metadata
                self.data_manager.update_item(item['id'], {
                    "lastConfidenceScore": confidence,
                    "lastConfidenceRating": rating
                })
                
                return {
                    "id": item['id'], 
                    "name": name, 
                    "price": price, 
                    "url": url, 
                    "status": "success",
                    "confidence": confidence,
                    "rating": rating
                }
            else:
                print(f"  No market listings found for {name} (Reason: {rating})")
                return {"id": item['id'], "name": name, "status": "no_listings", "message": rating}
        except Exception as e:
            print(f"  Error checking {name}: {e}")
            import traceback
            traceback.print_exc()
            return {"id": item['id'], "name": name, "status": "error", "message": str(e)}

scheduler = LegendastiqueScheduler()
