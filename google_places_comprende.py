import os
from re import split
from unittest import result
import requests
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_city_coordinates(city_name):
    """Converts a city name to Lat/Lng using Text Search (New)."""
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.location"
    }
    payload = {"textQuery": city_name}
    
    response = requests.post(url, headers=headers, json=payload).json()
    if "places" in response:
        return response["places"][0]["location"]
    return None

def find_nearby_airports(lat, lng, radius_km=10):
    """Finds airports within a specific radius using Nearby Search (New)."""
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.id,places.shortFormattedAddress"
    }
    
    # Radius must be in meters for the API
    radius_meters = 50000 # 50000m is limit
    
    payload = {
        "includedPrimaryTypes": ["airport"],
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius_meters
            }
        },
        "maxResultCount": 5 # Limit to top results
    }

    response = requests.post(url, headers=headers, json=payload).json()
    return response.get("places", [])



def get_100km_bounds(lat, lng):
    """
    Calculates a rough bounding box for a 100km radius.
    1 degree of latitude is ~111km. 
    """
    offset = 0.9  # Approximately 100km in degrees
    return {
        "low": {"latitude": lat - offset, "longitude": lng - offset},
        "high": {"latitude": lat + offset, "longitude": lng + offset}
    }

def get_city_coordinates_details_from_input(user_input):
    """
    1. Autocomplete the string 'agr' to 'Agra, UP, India'
    2. Get the Place ID for the first city match.
    3. Fetch coordinates using that Place ID.
    """
    # --- 1. Autocomplete Search ---
    auto_url = "https://places.googleapis.com/v1/places:autocomplete"
    auto_payload = {
        "input": user_input,
        "includedPrimaryTypes": ["(cities)"] # Restricts search to actual cities
    }
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": API_KEY}
    
    auto_res = requests.post(auto_url, headers=headers, json=auto_payload).json()
    suggestions = auto_res.get("suggestions", [])
    
    if not suggestions:
        return None, None, "No city found"
    suggests = {}
    # Grab the first match
    for suggestion in suggestions:
        first_suggestion = suggestion["placePrediction"]
        place_id = first_suggestion["placeId"]
        city_full_name = first_suggestion["text"]["text"]
        suggests[place_id] = {
                'place_id': place_id,
                'city_full_name': city_full_name,  
                'suggestion': first_suggestion
        }
    return suggests



def find_airports_100km_rect(city_name):
    # Unnao Coords
    lat, lng = 27.1767, 78.0081 
    bounds = get_100km_bounds(lat, lng)

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.id,places.location,places.addressComponents"
    }
    
    payload = {
        "textQuery": f"airports near {city_name}",
        "includedType": "airport",
        # Use locationRestriction with a RECTANGLE to bypass the 50km circle limit
        "locationRestriction": {
            "rectangle": bounds
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if "places" in data:
        places_data = {}
        print(f"Airports found within ~100km of {city_name}:")
        for place in data["places"]:
            
            name = place["displayName"]["text"]
            longText = {}
            for comp in place.get("addressComponents", []):
                if comp.get("types"):
                 longText[comp["types"][0]] = comp["longText"]
            places_data[place['id']] = {
                "name": name,
                "fullAddress": longText,
                "location":place['location']
            }
            print(f"- {name} [IATA: {longText}]")
        print(places_data)
        return places_data
    else:
        print("Error or No Results:", data)

def get_iata_from_coords(lat, lng):
    """Hits iatageo.com to get the 3-letter IATA code from coordinates."""
    try:
        url = f"http://iatageo.com/getCode/{lat}/{lng}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        print(f"Error fetching IATA: {e}")
    return "N/A"

def fetch_coords(place_id):
    """Single call to get location for one Place ID."""
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "id,location,displayName"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        return {"id": place_id, "error": str(e)}

def get_multiple_coords(place_ids):
    """Executes multiple requests in parallel."""
    # Using 5 workers to stay safe but fast
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_coords, place_ids))
    return results

def get_lat_long_iata_airport_data(place_id):
    """
    Worker function: 
    1. Fetches Lat/Lng from Google.
    2. Fetches IATA details from iatageo.
    """
    # 1. Get Coordinates from Google Places (New)
    google_url = f"https://places.googleapis.com/v1/places/{place_id}"
    google_headers = {
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "id,location,displayName"
    }
    
    try:
        g_res = requests.get(google_url, headers=google_headers, timeout=5).json()
        name = g_res.get("displayName", {}).get("text", "Unknown")
        loc = g_res.get("location", {})
        lat, lng = loc.get("latitude"), loc.get("longitude")

        if not lat or not lng:
            return {"id": place_id, "error": "No coordinates found"}

        # 2. Get IATA from iatageo using the coordinates found above
        iata_url = f"http://iatageo.com/getCode/{lat}/{lng}"
        i_res = requests.get(iata_url, timeout=5).json()
        
        return {
            "place_id": place_id,
            "name": name,
            "latitude": lat,
            "longitude": lng,
            "iata_data": i_res ,
            "iata": i_res.get("IATA") # Verified name from aviation database
        }
    except Exception as e:
        return {"id": place_id, "error": str(e)}

def batch_process_airports(places_id_list):
    """Processes all IDs in parallel to save time."""
    
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Map the worker function across the list of IDs
        future_to_data = {executor.submit(get_lat_long_iata_airport_data, pid): pid for pid in places_id_list}
           
    return future_to_data

def airport_search_in_text(user_input):
    """
    Returns only actual airport entities matching the input string.
    If 'Ujjain' is searched and has no airport, it returns [].
    """
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.location,places.formattedAddress,places.id"
    }

    payload = {
        "textQuery": f"airports starts with {user_input}",
        #"input": user_input, # This is the strict filter"
        "includedType": "airport", # This is the strict filter
        "maxResultCount": 5,
       # "rankPreference": "RELEVANCE"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        results = []
        response = response.json()
        for place in response.get("places", []):
            # Even with includedType, we verify via IATA to ensure 
            # we don't return bus stations or local landing strips.
            lat = place["location"]["latitude"]
            lng = place["location"]["longitude"]
            
            iata_code = get_iata_from_coords(lat, lng) # Using your existing function

            if iata_code and iata_code != "N/A":
                results.append({
                    "name": place["displayName"]["text"],
                    "iata": iata_code,
                    "address": place.get("formattedAddress"),
                    "location": place["location"]
                })

        return results
    except Exception as e:
        print(f"Error: {e}") 
        return []

def search_nearest_airports_from_city(city):
    '''
    Searches for nearest airports from a city name
    Parameters:
    city (str): The city name to search for.    
    '''
    suggestions = get_city_coordinates_details_from_input(city)
    places_id_list = list(suggestions.keys())
    results = {}
    future_to_data = batch_process_airports(places_id_list)
    for future in future_to_data:
            data = future.result()
            suggest_data = suggestions[data['place_id']]
            if "iata" in data:
                results[data["iata"]] = {'data':data,
                'city_full_name':suggest_data['city_full_name'],
                'district':suggest_data['suggestion']['structuredFormat']['mainText']['text']
                }
    return results

def get_airport_suggestions(user_input):
    """
      Search for airport suggestions based on user input in airport name
      Parameter:
         user_input: indi - for igi delhi
    """
    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
          "X-Goog-FieldMask":"*"
    }
    
    # We use 'airport' in the input string to bias results for 'amau'
    payload = {
        "input": user_input,
        "includedPrimaryTypes": ["airport"], # This restricts to real airports
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response = response.json()
        suggestions = response.get("suggestions", [])
        
        output = {}
         
        for s in suggestions:
            prediction = s["placePrediction"]
            #place_id_list.append(prediction["placeId"])
            output[prediction["placeId"]] = prediction["structuredFormat"] 
        
        places_id_list = list(output.keys())
        future_to_data = batch_process_airports(places_id_list)
        results = {}
        for future in future_to_data:
            data = future.result()
            #suggest_data = suggestions[data['place_id']]
            if "iata" in data:
                place_id = data['place_id'] 
                city_full_name = output[place_id]['secondaryText']['text']
                city_full_name_split = city_full_name.split(",")
                city_full_name= ", ".join(city_full_name_split[-3:])
                results[data["iata"]] = {'data':data,
                             'city_full_name': city_full_name}
        #res=get_multiple_coords(place_id_list)
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

 
if __name__ == "__main__":
    ist_of_matches = get_airport_suggestions("guna")
    #airport_search_in_text("mumb")
    #search_nearest_airports_from_city("Gun")
    #fetch_coords = get_multiple_coords(places_id_list)
    # bounded_airports = find_airports_100km_rect("Agra")
    # pid='ChIJoXMmTJ9BnDkRDbK-ggahXLE'
    # for k,v in data.items():
    #     lat,long = v['location']['latitude'],v['location']['longitude']
    #     v['airport_data'] = get_iata_from_coords(lat,long)
    # print(data)
    # coords = get_city_coordinates(city)
    
    # if coords:
    #     print(f"Coordinates for {city}: {coords}")
    #     airports = find_nearby_airports(coords['latitude'], coords['longitude'])
        
    #     print(f"\nAirports within 100km of {city}:")
    #     for ap in airports:
    #         name = ap['displayName']['text']
    #         address = ap.get('shortFormattedAddress', 'N/A')
    #         print(f"- {name} ({address})")
    # else:
    #     print("City not found.")