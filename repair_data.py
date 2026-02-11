import json
import os

DATA_FILE = 'data.json'

def repair_data():
    if not os.path.exists(DATA_FILE):
        print("No data file found.")
        return

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    updated_count = 0
    for item in data.get('items', []):
        # Check history for URL
        if 'priceHistory' in item and item['priceHistory']:
            # Sort just in case
            item['priceHistory'].sort(key=lambda x: x['date'])
            last_entry = item['priceHistory'][-1]
            
            if 'url' in last_entry and last_entry['url']:
                # Hoist it
                item['activeListingUrl'] = last_entry['url']
                updated_count += 1
                print(f"Hoisted URL for {item['name']}")

    if updated_count > 0:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully repaired {updated_count} items.")
    else:
        print("No items needed repair.")

if __name__ == "__main__":
    repair_data()
