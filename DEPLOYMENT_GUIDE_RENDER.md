# How to Deploy for FREE on Render.com

You asked for the **Cheapest** option.
**Render.com** is the best free option for this kind of app.

## Prerequisites
1.  **Push this code to GitHub** (I am doing this for you now).
2.  **Sign up for Render.com** (Login with GitHub).

## Step-by-Step Setup
1.  **Dashboard:** Go to your Render Dashboard.
2.  **New Web Service:** Click **"New +"** -> **"Web Service"**.
3.  **Connect GitHub:** Select "Build and deploy from a Git repository".
4.  **Select Repo:** Choose `LEGENDASTIQUE_EBAY_TRACKER`.
5.  **Settings:**
    *   **Name:** `legendastique-tracker` (or whatever you want)
    *   **Region:** Frankfurt (EU Central) or closest to you.
    *   **Branch:** `main`
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn server:app` (Render might auto-detect this because I added a `Procfile`).
    *   **Instance Type:** **Free**
6.  **Environment Variables (CRITICAL):**
    *   Scroll down to "Environment Variables".
    *   Click "Add Environment Variable".
    *   **Key:** `EBAY_APP_ID`  **Value:** (Your App ID from `.env`)
    *   **Key:** `EBAY_CERT_ID` **Value:** (Your Cert ID from `.env`)
7.  **Deploy:** Click **"Create Web Service"**.

## What happens next?
*   Render will download your code.
*   It will install Python and the libraries.
*   It will start your server.
*   It will give you a generic URL (e.g., `legendastique.onrender.com`).
*   **Done!** You can access that URL from your phone, laptop, anywhere.

## Note on "Free Tier"
*   The "Free" server goes to sleep after 15 minutes of inactivity.
*   The first time you load it after a while, it might take **30-50 seconds** to wake up. This is normal for free hosting.
