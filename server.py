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

@app.before_request
def log_request_info():
    logger.info(f"Incoming Request: {request.method} {request.path}")

@app.errorhandler(404)
def page_not_found(e):
    # Return JSON for API 404s, otherwise default HTML might be returned which breaks fetch
    if request.path.startswith('/api/'):
        return jsonify({"error": "Endpoint not found", "path": request.path}), 404
    return e # let Flask handle static 404s or return default HTML


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Serve specific static files only (not a catch-all)
@app.route('/<path:filename>.js')
@app.route('/<path:filename>.css')
@app.route('/<path:filename>.html')
@app.route('/<path:filename>.json')
@app.route('/<path:filename>.png')
@app.route('/<path:filename>.jpg')
@app.route('/<path:filename>.ico')
def serve_static_file(filename):
    """Serve static files with known extensions"""
    # Reconstruct the full filename with extension
    import re
    # Get the extension from the request path
    ext = re.search(r'\.(js|css|html|json|png|jpg|ico)$', filename)
    if ext:
        full_filename = filename
    else:
        # This shouldn't happen due to route matching, but just in case
        full_filename = filename + ext.group(0) if ext else filename
    
    if os.path.exists(full_filename):
        return send_from_directory('.', full_filename)
    return jsonify({"error": "File not found"}), 404


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
