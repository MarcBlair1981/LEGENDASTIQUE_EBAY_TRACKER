from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from data_manager import DataManager
from scheduler import scheduler
import os
import logging

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes
data_manager = DataManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return serve_index()

# --- API Endpoints ---

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify({"items": data_manager.get_items()})

@app.route('/api/items', methods=['POST'])
def add_item():
    item = request.json
    new_item = data_manager.add_item(item)
    return jsonify(new_item)

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item_full(item_id):
    """Update the entire item state (useful for history edits from frontend)"""
    updates = request.json
    updated_item = data_manager.update_item(item_id, updates)
    if updated_item:
        return jsonify(updated_item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    data_manager.delete_item(item_id)
    return jsonify({"success": True})


@app.route('/api/items/<int:item_id>/price', methods=['POST'])
def update_price(item_id):
    """Quick price update (simplified)"""
    data = request.json
    price = data.get('price')
    date = data.get('date') # Optional, defaults to now
    url = data.get('url')   # Optional
    
    if price is None:
        return jsonify({"error": "Price required"}), 400
        
    updated_item = data_manager.add_history_point(item_id, date, price, url)
    if updated_item:
        return jsonify(updated_item)
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/check-prices', methods=['POST'])
def trigger_check():
    """Manually trigger the background price check"""
    try:
        # We call the logic directly from the scheduler instance
        # Note: This runs synchronously in the request thread, which might take time if many items.
        results = scheduler.check_prices_manual()
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        print(f"Manual check failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/items/<int:item_id>/check', methods=['POST'])
def check_single_item(item_id):
    """Trigger price check for a single item"""
    print(f"\n=== CHECK SINGLE ITEM CALLED ===")
    print(f"Item ID: {item_id}")
    try:
        print(f"Calling scheduler.check_item_by_id({item_id})...")
        result = scheduler.check_item_by_id(item_id)
        print(f"Result: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"ERROR in check_single_item: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def run_server():
    print("Starting Legendastique Server on http://localhost:5000")
    
    # Start the automated background checker
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()
    
    app.run(port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    run_server()
