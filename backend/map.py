from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLEMAPS_API")


class LocationRequest(BaseModel):
    origin: str
    destination: str


@app.get("/directions/")
async def get_directions(origin: str, destination: str):
    """Fetch bus route details via Google Maps API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "transit",
        "key": GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail="Invalid request or API error")

    routes = []
    for route in data["routes"]:
        total_distance = sum(step["distance"]["value"] / 1000 for step in route["legs"][0]["steps"])  # km
        steps = [{"instruction": step["html_instructions"], "distance": step["distance"]["text"], "duration": step["duration"]["text"]}
                 for step in route["legs"][0]["steps"]]

        estimated_fare = round(total_distance * 15, 2)  # Assuming 15 NPR/km

        routes.append({
            "summary": route["summary"],
            "total_distance_km": total_distance,
            "estimated_fare": estimated_fare,
            "steps": steps
        })

    return {"routes": routes}
    