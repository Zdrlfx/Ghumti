from fastapi import FastAPI, HTTPException
import httpx
import os 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLEMAPS_API")

print(GOOGLE_MAPS_API_KEY)

@app.get("/staticmap/")
async def get_static_map(latitude: float, longitude: float, zoom: int = 14):
    """Returns a Google Static Map image URL based on latitude/longitude."""
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom={zoom}&size=600x400&maptype=roadmap&markers=color:red%7C{latitude},{longitude}&key={GOOGLE_MAPS_API_KEY}"
    
    return {"map_url": url}


@app.get("/geocode")
async def geocode(address: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail="Invalid address or API error")
    
    location = data["results"][0]["geometry"]["location"]
    return{"latitude": location["lat"], "longitude": location["lng"]}

@app.get("/directions/")
async def get_directions(origin: str, destination: str, alternatives: bool = True):
    """Fetch multiple route suggestions from Google Maps API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "alternatives": str(alternatives).lower(),  # Enables multiple routes
        "mode": "transit",  # Use "driving", "walking", "bicycling" if needed
        "key": GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail="Invalid request or API error")

    routes = []
    for route in data["routes"]:
        steps = []
        for step in route["legs"][0]["steps"]:
            steps.append({
                "instruction": step["html_instructions"],
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"]
            })
        
        routes.append({
            "summary": route["summary"],  # Route summary (e.g., road names)
            "steps": steps
        })

    return {"routes": routes}


