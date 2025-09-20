# Smart Bin FastAPI Backend

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

- POST `/garbage_alert` with JSON: `{ "bin_id": "bin1", "lat": 12.34, "lon": 56.78, "type": "Wet", "status": "FULL" }`
- GET `/bins` to get all bin statuses for the map.
