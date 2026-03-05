import csv
from bs4 import BeautifulSoup
import re
import logging,sys, json

from scrapper.scrap_config import HTML_FILE_PATH_CLEARTRIP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
# --- Configuration ---
 
 
OUTPUT_CSV_PATH = "flight_data_extracted.csv"

def write_html_to_file(html_content, filename="./scrapper/ss/ixigo_pretty.html"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

 

def parse_flight_data(data,uniquas):
    """Main function to run the script."""
    flights_data = []
    if not data:
        with open(HTML_FILE_PATH_CLEARTRIP.format(unqiuas=uniquas), 'r', encoding='utf-8') as f:
            file_data = f.read()
            file_data = json.loads(file_data)
    

    # Check if the required keys exist
    if not data or 'cards' not in data or 'J1' not in data['cards']:
        return flights_data

    all_cards = data['cards']
    journey_list = all_cards['J1']
    travel_options_fares = data.get("subTravelOptions", [])
    fares_list = data.get("fares", [])
    for card in journey_list:
        all_details = {}
        summary = card.get('summary', {})
        # 1. Basic Flight Info from Summary
        first_flight = summary.get('flights', [{}])[0]
        airline = first_flight.get('airlineCode')
        flight_no = first_flight.get('flightNumber')
        
        dep_info = summary.get('firstDeparture', {})
        dep_time = dep_info.get('airport', {}).get('time')
        departure_city = dep_info.get('airport', {}).get('code')
        
        arr_info = summary.get('lastArrival', {})
        arr_time = arr_info.get('airport', {}).get('time')
        arrival_city = arr_info.get('airport', {}).get('code')
        
        dur = summary.get('totalDuration', {})
        duration = f"{dur.get('hh')}h {dur.get('mm')}m"
        
        flight_type = summary.get('timelineText') # e.g., "Non-stop"
        
        # 2. Extract Layover Info
        layover_list = card.get('layover', [])
        layover_duration = ""
        layover_city = ""
        if layover_list:
            # Taking the first layover as an example
            l_dur = layover_list[0].get('duration', {})
            layover_duration = f"{l_dur.get('hh')}h {l_dur.get('mm')}m"
            layover_city = layover_list[0].get('airportCode')

        # 3. Extract Price and Offers from the specific travel option entry
        # Note: In Cleartrip JSON, detailed fare data is often keyed by the travelOptionId
        #option_details = all_cards.get(option_id, {})
        #fare_list = data.get('fares', [])
        
        price = None
        offers = []
        flight_offer = ""
         

        if fares_list:
            option_id = card.get('travelOptionId')
            fare_details = travel_options_fares.get(option_id, {})
            cheapest_fare_id = fare_details.get('cheapestFareId', '')
            cheapest_fare = fares_list.get(cheapest_fare_id, {})
            pricing = cheapest_fare.get('pricing', {})
            total_pricing = pricing.get('totalPricing', 0)
            price = total_pricing.get('totalPrice', 0)
            offers = total_pricing.get('message', 0)
            all_details['coupons'] = total_pricing.get('couponDetails', {})

        # 4. Compile the dictionary
        flights_data.append({
            'Airline': airline,
            'flight_no': f"{airline}{flight_no}",
            'Departure_Time': dep_time,
            'Departure_City': departure_city,
            'Duration': duration,
            'Arrival_Time': arr_time,
            'Arrival_City': arrival_city,
            'flight_type': flight_type,
            'Layover_Duration': layover_duration,
            'Layover_City': layover_city,
            'Price': price,
            'Offers': offers,
            'extra_badges': flight_offer,
            'source': 'cleartrip',
            'all_details': all_details  # Full data for this specific flight option
        })

    return flights_data


if __name__ == "__main__":
    parse_flight_data()