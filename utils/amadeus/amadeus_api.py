# Install the Python library from https://pypi.org/project/amadeus
from collections import defaultdict
from amadeus import Client, ResponseError
import os,requests,time
from dotenv import load_dotenv
dotenv_path = '.env'
CLIENT_ID='bHihfKzV7iI0WrtYIUG1IJLrAuPMOkYr',
CLIENT_SECRET='stg3N1M5tzGDFDXQ',
if not load_dotenv(dotenv_path):
    print(f"Warning: Could not find .env file at {dotenv_path}. Please ensure it exists and contains the necessary environment variables.")

    exit(1)
load_dotenv(dotenv_path)
HOSTNAME = 'test'
class AmadeusClient:
    def __init__(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, hostname=HOSTNAME):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = f"https://{hostname}.api.amadeus.com"
        self.token = None
        self.token_expiry = 0

    def _get_token(self):
        """Authenticates with Amadeus and stores the access token."""
        # Check if current token is still valid (with 10s buffer)
        if self.token and time.time() < self.token_expiry - 10:
            return self.token

        auth_url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(auth_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data['access_token']
            # expires_in is usually 1800 seconds (30 mins)
            self.token_expiry = time.time() + token_data['expires_in']
            return self.token
        else:
            raise Exception(f"Authentication failed: {response.text}")

    def get_flight_offers(self, origin='LKO', destination='DEL', departure_date='2026-01-20', return_date=None, adults=1):
        """Step 1: GET flight offers."""
        token = self._get_token()
        url = f"{self.base_url}/v2/shopping/flight-offers"
        
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'currencyCode': 'INR'
        }
        if return_date:
            params['returnDate'] = return_date

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Flight search failed: {response.text}")

    def predict_choice(self, flight_offers_json):
        """Step 2: POST to prediction endpoint using the search results."""
        token = self._get_token()
        url = f"{self.base_url}/v2/shopping/flight-offers/prediction"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        # Note: We send the entire result of the flight-offers search
        response = requests.post(url, headers=headers, json=flight_offers_json)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Prediction failed: {response.text}")

    def format_flight_data(self, raw_response):
        """
        Parses the raw Amadeus API response into your specific JSON format.
        """
        formatted_results = []
        
        # Extract dictionaries for lookup (Airline names, etc.)
        dictionaries = raw_response.get('dictionaries', {})
        airlines_dict = dictionaries.get('carriers', {})
        locations_dict = dictionaries.get('locations', {})

        for offer in raw_response.get('data', []):
            # We assume the first itinerary for simplicity
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            
            first_segment = segments[0]
            last_segment = segments[-1]
            
            # Basic info
            airline_code = first_segment['carrierCode']
            airline_name = airlines_dict.get(airline_code, airline_code)
            
            # Layovers logic
            layover_city = "None"
            layover_duration = "0"

            init_flight_no = f"{airline_code}{first_segment['number']}"
            if len(segments) > 1:
                
                init_flight_no = f"{airline_code}{first_segment['number']},{last_segment['carrierCode']}{last_segment['number']}"
                # First connection point
                layover_city = locations_dict.get(first_segment['arrival']['iataCode'], {}).get('cityCode', first_segment['arrival']['iataCode'])
                # You can calculate exact duration by subtracting arrival[0] from departure[1]
                layover_duration = "Multiple" if len(segments) > 2 else "1 Stop"

            # Construct the object in your requested format
            entry = {
                'Airline': airline_name,
                'flight_no': init_flight_no,
                'Departure_Time': first_segment['departure']['at'],
                'Departure_City': first_segment['departure']['iataCode'],
                'Arrival_Time': last_segment['arrival']['at'],
                'Arrival_City': last_segment['arrival']['iataCode'],
                'Layover_Duration': layover_duration,
                'Layover_City': layover_city,
                'flight_segments': segments,
                'Price': offer['price']['total'],
                'Offers': offer.get('lastTicketingDate', 'N/A'),
                'source': 'amadeus'
            }
            formatted_results.append(entry)
            
        return formatted_results
 


def get_flight_request(origin='LKO', destination='DEL', travel_date='2026-01-20'):
    import requests

    # CLIENT_ID = 'bHihfKzV7iI0WrtYIUG1IJLrAuPMOkYr'
    # # PASTE YOUR NEW REFRESHED SECRET HERE
    # CLIENT_SECRET = 'REPLACE_WITH_YOUR_NEW_SECRET' 

    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
    }

    response = requests.post(auth_url, data=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

def getflight():
    # Install the Python library from https://pypi.org/project/amadeus
    from amadeus import Client, ResponseError

    amadeus = Client(
        client_id='bHihfKzV7iI0WrtYIUG1IJLrAuPMOkYr',
        client_secret='stg3N1M5tzGDFDXQ',
        hostname='test'
    )

    try:
        '''
        Find the cheapest flights from SYD to BKK
        '''
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='LKO', 
            destinationLocationCode='DEL', departureDate='2026-01-20', adults=1)
        print(response.data)
    except ResponseError as error:
        raise error


def get_flight_dates(origin='DEL', destination='LKO', travel_date='2026-01-18'):
    client_id = os.environ.get("AMADEUS_KEY")
    client_secret = os.environ.get("AMADEUS_SECRET")
    amadeus = Client(
        client_id=client_id,
        client_secret=client_secret
    )

    try:
        '''
        Find cheapest dates from Delhi to Lucknow
        '''
        response = amadeus.shopping.flight_offers_search.get(originLocationCode=origin, 
                                                destinationLocationCode=destination,
                                                    departureDate=travel_date,
                                                    adults=1,
                                                   # currencyCode= "INR"
                                                    )
        print(response.data)
    except Exception as error:
        raise error

def get_amadeus_data(origin='LKO', destination='DEL', travel_date='2026-01-20'):
    amadeus = AmadeusClient()
    res = amadeus.get_flight_offers(origin, destination, travel_date)
    return amadeus.format_flight_data(res)

def source_flight_mapping(all_source_data):

    print(f"all_source_data: {all_source_data}")
    flight_data_dict = defaultdict(lambda: defaultdict(list))

    for source_list in all_source_data:
        if not source_list:
            continue
            
        for flight in source_list:
            f_no = str(flight.get('flight_no', '')).replace(" ", "").upper()
            src = flight.get('source')
            
            if f_no and src:
                flight_data_dict[f_no][src].append(flight)
    
    # 2. Convert to standard dict for JSON compatibility
    final_collection = {k: dict(v) for k, v in flight_data_dict.items()}
    return final_collection

if __name__ == "__main__":
#     #get_flight_dates()
    res = get_amadeus_data()
    source_flight_mapping([res])
    #  amadeus = AmadeusClient()
    #  res = amadeus.get_flight_offers()
    #  amadeus.format_flight_data(res)
