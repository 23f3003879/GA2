from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np, json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # Read telemetry bundle in the repo
    with open("telemetry.json") as f:
        telemetry = json.load(f)

    results = {}
    for region in regions:
        recs = telemetry.get(region, [])
        if not recs:
            continue
        lat = np.array([r["latency_ms"] for r in recs])
        up = np.array([r["uptime"] for r in recs])
        results[region] = {
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > threshold).sum()),
        }
    return results
