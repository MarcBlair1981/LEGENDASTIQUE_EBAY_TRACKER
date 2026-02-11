import json
import os
from datetime import datetime

DATA_FILE = 'data.json'

class DataManager:
    def __init__(self):
        self._load_data()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = {"items": []}
        else:
            self.data = {"items": []}

    def reload_data(self):
        """Force reload from disk to sync with other processes"""
        self._load_data()

    def _save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_items(self):
        self._load_data()
        return self.data.get("items", [])

    def add_item(self, item):
        self._load_data()
        # Ensure item has required fields
        if 'id' not in item:
            item['id'] = int(datetime.now().timestamp() * 1000)
        if 'priceHistory' not in item:
            item['priceHistory'] = [{'date': datetime.now().isoformat(), 'price': item.get('price', 0)}]
        
        self.data["items"].append(item)
        self._save_data()
        return item

    def delete_item(self, item_id):
        self.data["items"] = [i for i in self.data["items"] if i['id'] != item_id]
        self._save_data()

    def update_item(self, item_id, updates):
        self._load_data()
        for item in self.data["items"]:
            if item['id'] == item_id:
                item.update(updates)
                self._save_data()
                return item
        return None

    def add_history_point(self, item_id, date_str, price, url=None):
        for item in self.data["items"]:
            if item['id'] == item_id:
                if 'priceHistory' not in item:
                    item['priceHistory'] = []
                
                new_entry = {'date': date_str, 'price': price}
                if url:
                    new_entry['url'] = url
                    
                item['priceHistory'].append(new_entry)
                
                # Sort history
                item['priceHistory'].sort(key=lambda x: x['date'])
                
                # Update current price if this is the newest entry
                latest_entry = item['priceHistory'][-1]
                item['price'] = latest_entry['price']
                
                # Hoist URL for easier frontend access
                if url:
                    item['activeListingUrl'] = url
                
                self._save_data()
                return item
        return None

    def delete_history_point(self, item_id, index_in_sorted_list):
        # This mirrors the frontend logic, but backend should really use IDs for history points ideally.
        # For compatibility with current frontend logic which effectively sends "delete at index X",
        # we might need to adjust.
        # actually, the frontend might be easier to just send the *entire* updated item for now?
        # Let's support "Update Item" as a catch-all for now to be easiest for migration.
        pass
