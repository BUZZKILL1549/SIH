
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
from datetime import datetime


app = FastAPI()

# For Render: get port from environment variable
PORT = int(os.environ.get("PORT", 10000))

# Allow CORS for local Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "bins.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_id TEXT UNIQUE,
        lat REAL,
        lon REAL,
        type TEXT,
        status TEXT,
        last_update TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

class BinAlert(BaseModel):
    bin_id: str
    lat: float
    lon: float
    type: str  # 'Wet' or 'Dry'
    status: str  # 'FULL' or 'EMPTY'

@app.post("/garbage_alert")
def garbage_alert(alert: BinAlert):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO bins (bin_id, lat, lon, type, status, last_update)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(bin_id) DO UPDATE SET
            lat=excluded.lat,
            lon=excluded.lon,
            type=excluded.type,
            status=excluded.status,
            last_update=excluded.last_update
    """, (alert.bin_id, alert.lat, alert.lon, alert.type, alert.status, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Alert received"}

@app.get("/bins")
def get_bins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bin_id, lat, lon, type, status, last_update FROM bins")
    bins = [
        {
            "bin_id": row[0],
            "lat": row[1],
            "lon": row[2],
            "type": row[3],
            "status": row[4],
            "last_update": row[5],
        }
        for row in c.fetchall()
    ]
    conn.close()
    return bins
