import os
import requests
import base64
import time
from dotenv import load_dotenv

load_dotenv()

class EbayClient:
    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.env = os.getenv("EBAY_ENV", "PRODUCTION").upper()
        
        if self.env == "SANDBOX":
            self.oauth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            self.browse_url = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"
            self.scope = "https://api.ebay.com/oauth/api_scope"
        else:
            self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            self.browse_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
            self.scope = "https://api.ebay.com/oauth/api_scope"

        self.access_token = None
        self.token_expiry = 0

    def get_access_token(self):
        """Generates or returns a valid OAuth Application Access Token"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        try:
            credential = f"{self.app_id}:{self.cert_id}"
            encoded_cred = base64.b64encode(credential.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_cred}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "client_credentials",
                "scope": self.scope
            }

            response = requests.post(self.oauth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            # safely subtract buffer from expiry
            self.token_expiry = time.time() + int(token_data.get('expires_in', 7200)) - 60
            
            return self.access_token
            
        except Exception as e:
            print(f"Error getting OAuth token: {e}")
            return None

    def get_last_sold_price(self, query, exclude_keywords=None):
        """
        Fetches the MOST RECENT Sold Price for an item using the Finding API.
        Returns: (price, date_str, url)
        """
        # Finding API Endpoint
        if self.env == "SANDBOX":
            url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"
        else:
            url = "https://svcs.ebay.com/services/search/FindingService/v1"

        # Construct Query with exclusions
        full_query = query
        if exclude_keywords:
            for word in exclude_keywords:
                if word.strip():
                    full_query += f" -{word.strip()}"

        # Finding API uses URL parameters, not JSON body
        params = {
            "OPERATION-NAME": "findCompletedItems",
            "SERVICE-VERSION": "1.0.0",
            "SECURITY-APPNAME": self.app_id,
            "RESPONSE-DATA-FORMAT": "JSON",
            "REST-PAYLOAD": "",
            "keywords": full_query,
            "GLOBAL-ID": "EBAY-GB",  # UK marketplace
            "sortOrder": "EndTimeSoonest",
            "paginationInput.entriesPerPage": "1",
            "itemFilter(0).name": "SoldItemsOnly",
            "itemFilter(0).value": "true"
        }

        try:
            print(f"DEBUG: Finding Sold Items for '{query}'...")
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Finding API Error ({response.status_code}): {response.text}")
                return None, None, None

            data = response.json()
            
            # Check for API-level errors
            if "errorMessage" in data:
                print(f"Finding API Error: {data['errorMessage']}")
                return None, None, None
            
            # Navigate JSON response: findCompletedItemsResponse -> searchResult -> item
            search_result = data.get("findCompletedItemsResponse", [{}])[0].get("searchResult", [{}])[0]
            count = int(search_result.get("@count", "0"))

            if count > 0:
                item = search_result.get("item", [])[0]
                
                # Get Price
                selling_status = item.get("sellingStatus", [{}])[0]
                price_obj = selling_status.get("currentPrice", [{}])[0]
                price = float(price_obj.get("__value__", 0.0))
                
                # Get Date
                listing_info = item.get("listingInfo", [{}])[0]
                date_str = listing_info.get("endTime", [None])[0]
                
                title = item.get("title", ["Unknown"])[0]
                view_item_url = item.get("viewItemURL", ["#"])[0]

                print(f"Found SOLD item: {title} for £{price} on {date_str}")
                return price, date_str, view_item_url
            else:
                print(f"No sold listings found for '{query}'")
                return None, None, None

        except Exception as e:
            print(f"Finding API failed: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
