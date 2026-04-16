"""
Cooling System Dashboard - Flask Backend
Production-ready API for serving CSV data to frontend dashboard
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all origins (frontend dashboard)
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "data.csv"))
REFRESH_INTERVAL = 5  # seconds

# Expected CSV columns
CSV_COLUMNS = [
    "timestamp",
    "chiller_temp_in",
    "chiller_temp_out",
    "cooling_tower_temp",
    "humidity",
    "pressure",
    "status"
]

# Global state
data_cache = []
cache_lock = threading.Lock()
last_modified_time = 0


def parse_csv_safe(file_path):
    """
    Safely parse CSV with error handling and column validation.
    Returns list of dict records or empty list on error.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            return []

        # Read CSV with explicit column names
        df = pd.read_csv(file_path, header=None, names=CSV_COLUMNS)

        # Validate required columns exist
        missing_cols = set(["timestamp", "chiller_temp_in", "chiller_temp_out", "status"]) - set(df.columns)
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return []

        # Convert numeric columns, coerce errors to NaN then fill
        numeric_cols = ["chiller_temp_in", "chiller_temp_out", "cooling_tower_temp", "humidity", "pressure"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows where critical fields are NaN
        df = df.dropna(subset=["chiller_temp_in", "chiller_temp_out", "status"])

        # Convert to dict records
        records = df.to_dict(orient='records')
        logger.info(f"Successfully parsed {len(records)} records from CSV")
        return records

    except pd.errors.EmptyDataError:
        logger.warning("CSV file is empty")
        return []
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        return []


def load_data():
    """Load data from CSV into cache."""
    global data_cache, last_modified_time

    try:
        current_mtime = os.path.getmtime(FILE_PATH) if os.path.exists(FILE_PATH) else 0

        # Only reload if file has changed
        if current_mtime != last_modified_time:
            records = parse_csv_safe(FILE_PATH)
            with cache_lock:
                data_cache = records
            last_modified_time = current_mtime
            logger.info(f"Cache updated with {len(records)} records")

    except Exception as e:
        logger.error(f"Error in load_data: {e}")


def auto_refresh():
    """Background thread to periodically refresh data."""
    while True:
        load_data()
        time.sleep(REFRESH_INTERVAL)


def create_response(data, status_code=200):
    """
    Create standardized API response envelope.
    Format: {"data": ..., "count": n}
    """
    response = {
        "data": data if data is not None else [],
        "count": len(data) if isinstance(data, list) else (1 if data else 0),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return jsonify(response), status_code


def create_error_response(message, status_code=500):
    """Create standardized error response."""
    response = {
        "data": None,
        "count": 0,
        "error": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return jsonify(response), status_code


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    with cache_lock:
        has_data = len(data_cache) > 0

    return jsonify({
        "status": "healthy" if has_data else "degraded",
        "records_cached": len(data_cache),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


# Get all data
@app.route("/all", methods=["GET"])
def all_data():
    """
    GET /all - Return all records from CSV.
    Response: {"data": [...], "count": n}
    """
    with cache_lock:
        if not data_cache:
            return create_error_response("No data available", 404)
        return create_response(data_cache.copy())


# Get latest record
@app.route("/latest", methods=["GET"])
def latest():
    """
    GET /latest - Return most recent record.
    Response: {"data": {...}, "count": 1}
    """
    with cache_lock:
        if not data_cache:
            return create_error_response("No data available", 404)
        return create_response(data_cache[-1])


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return create_error_response("Endpoint not found", 404)


@app.errorhandler(500)
def server_error(error):
    return create_error_response("Internal server error", 500)


# Initialize and start
if __name__ == "__main__":
    # Initial load
    load_data()

    # Start background refresh thread
    refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
    refresh_thread.start()
    logger.info("Background refresh thread started")

    # Run Flask server
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
