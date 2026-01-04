import csv
from bs4 import BeautifulSoup
import re
import logging,sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
# --- Configuration ---
HTML_FILE_PATH = "./scrapper/ss/mmt_res_expedia.html"
OUTPUT_CSV_PATH = "flight_data_extracted.csv"


def write_html_to_file(html_content, filename="./scrapper/ss/mmt_pretty.html"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def extract_flight_data(html_content):
    """
    Parses the HTML content to extract flight details using Beautiful Soup.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html_string = soup.prettify()
    write_html_to_file(pretty_html_string)
    flight_data = []
    flight_html = soup.find_all('li',attrs={"data-test-id":"offer-listing"})
    for flight in flight_html:
        try:
            secondary_section = flight.find('div', {'data-stid': 'secondary-section'})
            route = "N/A"
            airline = "N/A"
            if secondary_section:
                labels = secondary_section.find_all('div', class_='truncate-lines-2')
                if len(labels) >= 2:
                    route = labels[0].get_text(strip=True)   # e.g., "Lucknow (LKO) - Delhi (DEL)"
                    airline = labels[1].get_text(strip=True) # e.g., "IndiGo"
                    departure_city = route.split(" - ")[0]
                    arrival_city = route.split(" - ")[1]
            # tertiary-section
            tertiary_section = flight.find('div', {'data-stid': 'tertiary-section'})
            duration = None
            stops = None
            if tertiary_section:
                # tertiary_section.find_all('span')Find all divs with 'uitk-text' - this is specific to the route/airline labels
                labels = tertiary_section.find_all('span' )
                if len(labels) >= 3:
                    duration = labels[0].get_text(strip=True)   # e.g., duration of time like 1h 15m
                    stops = labels[2].get_text(strip=True) # e.g., "IndiGo"
                layover_duration,layover_city=None,None
                if stops != "Direct":
                    divForStops = tertiary_section.find_all('div', class_="truncate-lines-2")
                    layover_details = divForStops[0].get_text(strip=True) #'1h 35m in DED'
                    layover_duration = layover_details.split(" in ")[0]
                    layover_city = layover_details.split(" in ")[1]
            #  Extract Times (using classes)
            times = flight.find_all('div', class_='step-indicator-brand-color-time')
            dep_time = times[0].get_text(strip=True) if len(times) > 0 else "N/A"
            arr_time = times[1].get_text(strip=True) if len(times) > 1 else "N/A"
            
            #Price Section 
            price_section = flight.find('div', {'data-stid':"price-column"})
            if price_section:
                price_element = price_section.find_all('span')
                if len(price_element) == 2:
                    price_element = price_element[1].get_text(strip=True)
                elif len(price_element) > 2:
                    seats_left = price_element[0].get_text(strip=True) 
                    price_element = price_element[2].get_text(strip=True)   


            logger.info(flight,route,airline,dep_time,arr_time,duration,stops)
            flight_data.append({
                    'Airline': airline,
                    'Departure_Time': dep_time,
                    'Departure_City': departure_city,
                    'Arrival_Time': arr_time,
                    'Arrival_City': arrival_city,
                    'Layover_Duration': layover_duration,
                    'Layover_City': layover_city,
                    'Price': price_element,
                    
                    'Offers': None,
                    'source': 'expedia'

                })
        except Exception as e:
            logger.info(f"Error processing flight: {e}")
             
    return flight_data

def save_to_csv(data, filename):
    """Saves the extracted data to a CSV file."""
    if not data:
        print("No data to save.")
        return

    fieldnames = list(data[0].keys())
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"\nSuccessfully extracted {len(data)} flights and saved to {filename}")
    except Exception as e:
        logger.info(f"Error saving to CSV: {e}")


def parse_flight_data():
    """Main function to run the script."""
    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        logger.info(f"Error: The file '{HTML_FILE_PATH}' was not found.")
        logger.info("Please ensure the script is in the same directory as 'mmt_res.html'.")
        return
    except Exception as e:
        logger.info(f"Error reading file: {e}")
        return

    flight_data = extract_flight_data(html_content)
    return flight_data
    #save_to_csv(flight_data, OUTPUT_CSV_PATH)


if __name__ == "__main__":
    parse_flight_data()