# How to Get Your eBay Developer Keys

To allow Legendastique to check prices automatically, you need a free eBay Developer Account.

## Step 1: Register
1.  Go to [https://developer.ebay.com/signin](https://developer.ebay.com/signin) and sign in with your normal eBay account.
2.  Agree to the terms to create a Developer Account.
3.  Fill in the application details (you can just say "Personal Project" or "Collector Tools").

## Step 2: Create Keys
1.  Once logged in, go to your **"Hi [Name]"** menu -> **Application Access Keys**.
2.  You will see two columns: **Sandbox** and **Production**.
3.  Under **Production** (so we can see real live prices), click **Create a keyset**.
4.  It may ask for a primary contact; just fill in your details.

## Step 3: Get the IDs
1.  After creating the keyset, look for the **App ID (Client ID)**. It's a long string of characters.
2.  Look for the **Cert ID (Client Secret)**. You might need to click "Show".

## Step 4: Add to Legendastique
Create a file named `.env` in the `triple-radiation` folder with the following content:

```env
EBAY_APP_ID=YOUR_APP_ID_HERE
EBAY_CERT_ID=YOUR_CERT_ID_HERE
```

Replace `YOUR_APP_ID_HERE` and `YOUR_CERT_ID_HERE` with the actual codes you got.
