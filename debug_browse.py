from ebay_client import EbayClient
import logging

# Set up logging to console to see what's happening inside EbayClient if it has prints
logging.basicConfig(level=logging.DEBUG)

def test_specific_items():
    client = EbayClient()
    
    items_to_test = [
        "PSA",
        "2026 Topps Chrome Premier League Hobby"
    ]
    
    print("--- Starting Debug Session ---")
    
    # Check Token First
    token = client.get_access_token()
    if token:
        print(f"Token acquired: {token[:10]}...")
    else:
        print("CRITICAL: Failed to get OAuth Token")
        return

    for query in items_to_test:
        print(f"\nTesting Query: '{query}'")
        try:
            price, date, url = client.get_lowest_price(query)
            if price:
                print(f"SUCCESS: Found £{price}")
                print(f"URL: {url}")
            else:
                print("FAILURE: No items found.")
        except Exception as e:
            print(f"EXCEPTION: {e}")

    print("\n--- End Debug Session ---")

if __name__ == "__main__":
    test_specific_items()
