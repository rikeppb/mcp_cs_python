from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate
from typing import Optional, Tuple

import requests

# === Converts from array of points from openStreet to geojson MULTIPOINT  ===
import json

def convert_to_multipoint_geojson(osm_results: str):
    # Extract coordinates (lon, lat) for MultiPoint (GeoJSON expects [lon, lat])
    coordinates = [
        [float(item["lon"]), float(item["lat"])]
        for item in osm_results
        if "lon" in item and "lat" in item
    ]
    
    # Base GeoJSON structure
    geojson_template = {
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "MultiPoint",
                    "coordinates": coordinates  # Replace with extracted coordinates
                },
                "properties": {
                    "advancedFilters": [
                        {
                            "service": ["EV_CHARGING"]
                        }
                    ]
                }
            }
        ],
        "type": "FeatureCollection"
    }

    return geojson_template

def geolocation_mcp(query: str):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    response = requests.get(url).json()
    if response:
        return f"City {query} not found "
    return convert_to_multipoint_geojson(response)

def geolocation_mcp(query: str) -> Optional[Tuple[float, float]]:
    known_locations = {
        "paris": (48.8566, 2.3522),
        "new york": (40.7128, -74.0060),
        "berlin": (52.52, 13.4050),
    }
    for name, coords in known_locations.items():
        if name in query.lower():
            return coords
    return None

def charging_station_mcp(lat: float, lon: float) -> Optional[str]:
    dummy_stations = {
        (48.8566, 2.3522): ["ChargePoint A - Paris", "FastCharge Station B - Paris"],
        (40.7128, -74.0060): ["EVGo - NYC Midtown", "Tesla Supercharger - Brooklyn"],
    }
    return dummy_stations.get((lat, lon), None)


# === LangChain Tools ===

def geo_tool(input_text: str) -> str:
    coords = geolocation_mcp(input_text)
    if coords:
        return f"Coordinates: {coords[0]}, {coords[1]}"
    else:
        return "No location found."

def station_tool(input_text: str) -> str:
    coords = geolocation_mcp(input_text)
    if not coords:
        return "No street or country found with that name."

    lat, lon = coords
    stations = charging_station_mcp(lat, lon)
    if not stations:
        return "No charging stations were found at that location."
    return f"Charging stations near {lat},{lon}:\n" + "\n".join(stations)


# === Natural Language Processing Logic ===

def is_charging_request(text: str) -> bool:
    return bool(re.search(r'\bcharging station(s)?\b', text, re.IGNORECASE))


# === Application Entry ===

def main():
    llm = ChatOpenAI(temperature=0, model="gpt-4")

    tools = [
        Tool(name="GeolocationTool", func=geo_tool, description="Find coordinates from a country or street."),
        Tool(name="ChargingStationTool", func=station_tool, description="Get charging stations near a location.")
    ]

    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    user_input = input("Where or what are you looking for? (e.g., 'charging stations in Berlin')\n> ")

    if is_charging_request(user_input):
        response = station_tool(user_input)
    else:
        response = geo_tool(user_input)

    print(f"\n🧠 Response: {response}")


if __name__ == "__main__":
    main()