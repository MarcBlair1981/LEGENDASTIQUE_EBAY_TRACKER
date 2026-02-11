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

    def get_lowest_price(self, query):
        """
        Fetches the LOWEST Active 'Buy It Now' price for an item.
        Effective for determining current market floor.
        Returns: (price, date_str, url)
        """
        token = self.get_access_token()
        if not token:
            return None, None, None

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB" 
        }

        # Search for Fixed Price items, sort by Price Ascending
        params = {
            "q": query,
            "filter": "buyingOptions:{FIXED_PRICE}", 
            "sort": "price", 
            "limit": 1
        }

        try:
            print(f"DEBUG: Browsing for '{query}' (Active Listings)...")
            response = requests.get(self.browse_url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"Browse API Error: {response.text}")
                return None, None, None

            data = response.json()
            
            if "itemSummaries" in data and len(data["itemSummaries"]) > 0:
                item = data["itemSummaries"][0]
                
                # Get Price
                price_obj = item.get("price", {})
                price = float(price_obj.get("value", 0.0))
                
                # Use current time as "valuation date" since it's an active listing check
                from datetime import datetime
                date_str = datetime.now().isoformat()
                
                url = item.get("itemWebUrl")
                title = item.get("title")

                print(f"Found active item: {title} for £{price}")
                return price, date_str, url
            else:
                print(f"No active listings found for '{query}'")
                return None, None, None

        except Exception as e:
            print(f"Browse API failed: {e}")
            return None, None, None
