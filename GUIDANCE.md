# Handover Guide: Legendastique Tracker

## Current Status
*   **Codebase:** Fully functional.
*   **Backend:** Python/Flask server with atomic data saving (fixed the data loss bug).
*   **Frontend:** Vanilla JS (`app.js`) with responsive design and charts.
*   **Data:** Persisted in `data.json`.
*   **eBay:** Connected via `ebay_client.py` using OAuth (Client Credentials).

## How to Resume Work
1.  **Start the Server:** Always run `python server.py` first.
2.  **Access App:** Open `http://localhost:5000`.
3.  **Add Items:** Use the "+ Add Item" button. Be specific with names (e.g., "1986 Fleer Michael Jordan #57 PSA 8") for better price matching.

## GitHub instructions
To save this project to your GitHub:

1.  **Create a New Repository** on GitHub (e.g., named `legendastique-tracker`).
2.  **Run these commands** in your terminal (inside this folder):
    ```bash
    git init
    git add .
    git commit -m "Initial commit of Legendastique Tracker v5"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/legendastique-tracker.git
    git push -u origin main
    ```

## Why GitHub Pages Won't Work (Fully)
You asked to use GitHub Pages.
*   **The Problem:** GitHub Pages is for **static websites** only. It cannot run Python code (`server.py`).
*   **The Result:** If you push this to Pages, the website will load, but it will show "Loading..." forever or "Error" because it cannot talk to the Python backend to get prices or save data.
*   **The Solution:** You need a "Dynamic App Host".
    *   **Render.com** (Free tier available for Python web services).
    *   **PythonAnywhere** (Easiest for beginners).
    *   **Railway.app** (Very user friendly).

For now, running it locally (`localhost:5000`) is the best way to keep it free and fully functional.
