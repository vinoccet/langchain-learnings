import requests
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Define your SerpApi API Key
# Sign up at https://serpapi.com to get your free key
SERPAPI_API_KEY = os.getenv("SERP_API_KEY")

# 2. Configure the Google Flights search parameters
# Required: engine, departure_id, arrival_id, outbound_date
params = {
    "engine": "google_flights",
    "departure_id": "MAA",         # Airport code (Austin-Bergstrom International)
    "arrival_id": "SIN",           # Airport code (Los Angeles International)
    "outbound_date": "2026-10-22", # Date in YYYY-MM-DD format
    "return_date": "2026-10-29",   # Optional: Include for round-trip flights
    "currency": "INR",             # Optional: Currency definition
    "hl": "en",                    # Optional: Language profile
    "api_key": SERPAPI_API_KEY
}

try:
    # 3. Make the GET request to SerpApi's central endpoint
    print("Fetching flight data from SerpApi...")
    response = requests.get("https://serpapi.com/search", params=params)
    
    # Check if the HTTP request was successful
    response.raise_for_status()
    
    # 4. Parse the response into a JSON directory
    data = response.json()
    
    # 5. Extract and print flight details
    # SerpApi categorizes results into 'best_flights' and 'other_flights'
    best_flights = data.get("best_flights", [])
    
    if not best_flights:
        print("No flight information found or check your parameters.")
    else:
        print(f"\n--- Top {len(best_flights)} Best Flight Options ---")
        for index, itinerary in enumerate(best_flights, start=1):
            price = itinerary.get("price")
            total_duration = itinerary.get("total_duration")
            
            print(f"\nOption #{index}: Total Price: ${price} | Duration: {total_duration} mins")
            
            # A single itinerary option can contain layovers (multiple leg flights)
            for leg in itinerary.get("flights", []):
                airline = leg.get("airline")
                flight_number = leg.get("flight_number")
                dep_airport = leg.get("departure_airport", {}).get("id")
                dep_time = leg.get("departure_airport", {}).get("time")
                arr_airport = leg.get("arrival_airport", {}).get("id")
                arr_time = leg.get("arrival_airport", {}).get("time")
                
                print(f"  ✈️ {airline} ({flight_number}): {dep_airport} ({dep_time}) -> {arr_airport} ({arr_time})")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")