# Legendastique Collectibles Tracker

A modern web application for tracking the value of collectibles (cards, wax, magazines) with real-time eBay price integration.

![Screenshot](screenshot.png)

## Features
*   **Portfolio Tracking:** Track total value and item count.
*   **Authentic eBay Data:** Fetches the lowest active "Buy It Now" price from eBay to give you a realistic "Market Floor" valuation.
*   **Visual Charts:** Interactive svg charts for portfolio and item history.
*   **Activity Feed:** See a history of price changes with direct links to eBay listings.
*   **Direct Links:** "View Listing" button takes you straight to the specific eBay item found.

## Setup & Running Locally

1.  **Install Python:** Ensure you have Python 3.9+ installed.
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure API Keys:**
    *   Create a `.env` file in this directory.
    *   Add your eBay Developer credentials:
        ```
        EBAY_APP_ID=your_app_id
        EBAY_CERT_ID=your_cert_id
        ```
4.  **Run the Server:**
    ```bash
    python server.py
    ```
5.  **Open the App:**
    *   Go to `http://localhost:5000` in your browser.

## 🛑 Common Mistakes (Read This!)
*   **DO NOT double-click `index.html`** in your file folder. It will open as a file (`file:///`) and **will not work**. The app needs the Python server to be running.
*   **Always leave the black terminal window open** while using the app. If you close it, the server stops.

## 💻 How to Run on a New PC
If you download this code to a new computer:
1.  **Install Python** from python.org.
2.  **Open Terminal/Command Prompt** in the project folder.
3.  **Install Libraries:** `pip install -r requirements.txt`
4.  **Create your keys:** Make a new `.env` file with your eBay keys (see Setup above).
5.  **Start App:** Type `python server.py`.
6.  **Use App:** Open `http://localhost:5000`.

## Deployment Notes

**Important:** This application requires a Python backend to run. **It cannot be hosted fully on GitHub Pages.**

*   **GitHub Pages** only hosts static files (HTML/CSS/JS). If you upload this there, you will see the design, but the "Check Prices" button and data loading will **FAIL** because there is no server to run the Python code.
*   **Recommended Host:** Use a service like **Render**, **Railway**, or **PythonAnywhere** to host the full application (Backend + Frontend).

## Project Structure
*   `server.py`: Flask backend API.
*   `scheduler.py`: Handles background price checking logic.
*   `ebay_client.py`: Intefaces with eBay Browse API.
*   `app.js`: Main frontend logic (rendering, charts, state).
*   `data_manager.py`: Handles data persistence to `data.json`.
*   `data.json`: Database file storing your items and history.
