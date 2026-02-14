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

    def get_lowest_market_price(self, query, exclude_keywords=None, global_exclusions=None):
        """
        Fetches the LOWEST Active 'Buy It Now' price from OTHER SELLERS.
        Excludes listings from 'legendastique' to get true market price.
        Returns: (price, date_str, url, confidence, rating)
        """
        token = self.get_access_token()
        if not token:
            return None, None, None, 0, "No Token"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB" 
        }

        # Construct Query with Exclusions
        full_query = query
        
        # Exclude the user's own seller name
        full_query += " -legendastique"
        
        # Add user-defined exclusions (specific to item)
        if exclude_keywords:
            for word in exclude_keywords:
                if word.strip():
                    full_query += f" -{word.strip()}"

        # Add global exclusions
        if global_exclusions:
            g_parts = []
            if isinstance(global_exclusions, str):
                # Prefer comma separation for phrases
                if ',' in global_exclusions:
                    g_parts = [p.strip() for p in global_exclusions.split(',') if p.strip()]
                else:
                    g_parts = global_exclusions.split()
            elif isinstance(global_exclusions, list):
                g_parts = global_exclusions
            
            for word in g_parts:
                if word.strip():
                    # If phrase contains space, quote it to prevent splitting
                    if ' ' in word:
                         full_query += f' -"{word.strip()}"'
                    else:
                         full_query += f' -{word.strip()}'

        # Search for Fixed Price items, sort by Price Ascending
        params = {
            "q": full_query,
            "filter": "buyingOptions:{FIXED_PRICE}", 
            "sort": "price", 
            "limit": 10  # Get top 10 for confidence analysis
        }

        try:
            print(f"DEBUG: Searching market price for '{query}' (excluding legendastique)...")
            
            response = requests.get(self.browse_url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"Browse API Error ({response.status_code}): {response.text[:500]}")
                return None, None, None, 0, "API Error"

            data = response.json()
            
            # Check for API errors
            if "errors" in data:
                print(f"API returned errors: {data['errors']}")
                return None, None, None, 0, "API Error"
            
            # Log total found (useful for debugging 0 results)
            total = data.get('total', 0)
            print(f"DEBUG: API reported {total} total matches for query.")

            if "itemSummaries" in data and len(data["itemSummaries"]) > 0:
                # Filter out any remaining legendastique listings
                valid_items = [
                    item for item in data["itemSummaries"]
                    if "legendastique" not in item.get("seller", {}).get("username", "").lower()
                ]
                
                count = len(valid_items)
                print(f"DEBUG: Found {len(data['itemSummaries'])} total, {count} valid items")
                
                if not valid_items:
                    print(f"  No listings found from other sellers for {query}")
                    return None, None, None, 0, "No listings found (all excluded)"
                
                # --- CONFIDENCE SCORING LOGIC ---
                confidence = 0
                reasons = []
                
                # 1. Volume Score (30%)
                if count >= 5: confidence += 30
                elif count >= 3: confidence += 20
                elif count >= 1: confidence += 10
                reasons.append(f"Found {count} items")

                # 2. Price Consistency Score (50%)
                item = valid_items[0]
                price_obj = item.get("price", {})
                price = float(price_obj.get("value", 0.0))
                
                if count > 1:
                    others = valid_items[1:4] # Get next 3
                    other_prices = [float(i.get("price", {}).get("value", 0)) for i in others]
                    if other_prices:
                        avg_other = sum(other_prices) / len(other_prices)
                        ratio = price / avg_other
                        if ratio > 0.8: confidence += 50
                        elif ratio > 0.5: confidence += 30
                        else: confidence += 0 # Outlier
                else:
                    confidence += 10 # Single item

                # 3. Keyword Match Score (20%)
                title = item.get("title", "").lower()
                query_words = [w.lower() for w in query.split()]
                if query_words:
                    matched_words = sum(1 for w in query_words if w in title)
                    match_pct = matched_words / len(query_words)
                    if match_pct == 1.0: confidence += 20
                    elif match_pct > 0.5: confidence += 10
                
                confidence = min(100, confidence)
                rating = "High" if confidence >= 80 else ("Medium" if confidence >= 50 else "Low")
                
                # Use current time
                from datetime import datetime
                date_str = datetime.now().isoformat()
                url = item.get("itemWebUrl")

                print(f"  Found: {item.get('title')} for £{price} | Confidence: {confidence}% ({rating})")
                return price, date_str, url, confidence, rating

            else:
                print(f"  No active listings found for {query}")
                print(f"  Response data: {str(data)[:200]}")
                return None, None, None, 0, "No results"

        except Exception as e:
            print(f"Browse API failed with exception: {e}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None, None, None, 0, f"Error: {str(e)}"
