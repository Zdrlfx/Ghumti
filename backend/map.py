from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# Allow frontend (Vite) to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLEMAPS_API")


class LocationRequest(BaseModel):
    origin: str
    destination: str


@app.get("/geocode")
async def geocode(address: str):
    """Get latitude and longitude of a location (bus stop)."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail="Invalid address or API error")
    
    location = data["results"][0]["geometry"]["location"]
    return {"latitude": location["lat"], "longitude": location["lng"]}


@app.get("/directions/")
async def get_directions(origin: str, destination: str):
    """Fetch route details, distance, and estimated fare using Google Maps API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "transit",  # Use bus transit mode
        "key": GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail="Invalid request or API error")

    routes = []
    for route in data["routes"]:
        total_distance = 0
        steps = []
        
        for step in route["legs"][0]["steps"]:
            step_distance = step["distance"]["value"] / 1000  # Convert meters to km
            total_distance += step_distance

            steps.append({
                "instruction": step["html_instructions"],
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"]
            })

        # Fare Calculation (Assuming a fare rate per km)
        fare_per_km = 15  # Adjust this based on real bus fares
        estimated_fare = round(total_distance * fare_per_km, 2)

        routes.append({
            "summary": route["summary"],  # Route summary (e.g., road names)
            "total_distance_km": total_distance,
            "estimated_fare": estimated_fare,
            "steps": steps
        })

    return {"routes": routes}
