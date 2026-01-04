import csv
from bs4 import BeautifulSoup
import re
import logging,sys

from scrapper.scrap_config import HTML_FILE_PATH_IXIGO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
# --- Configuration ---
HTML_FILE_PATH_IXIGO
# HTML_FILE_PATH = ["./scrapper/ss/mmt_res_0.html",
#                     "./scrapper/ss/mmt_res_1000.html",
#                     "./scrapper/ss/mmt_res_2000.html",
#                     "./scrapper/ss/mmt_res_3000.html",
#                     "./scrapper/ss/mmt_res_4000.html",
#                     "./scrapper/ss/mmt_res_5000.html",
#                     "./scrapper/ss/mmt_res_6000.html",
#                     "./scrapper/ss/mmt_res_7000.html",
#                     ]
OUTPUT_CSV_PATH = "flight_data_extracted.csv"

def write_html_to_file(html_content, filename="./scrapper/ss/ixigo_pretty.html"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def extract_flight_data(html_content,index):
    """
    Parses the HTML content to extract flight details using Beautiful Soup.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html_string = soup.prettify()
    write_html_to_file(pretty_html_string)
    flights_data = []
    logger.info(index)
    flight_listings = soup.find_all('div', class_='shadow-card')
    flight_listings = flight_listings[1:]
    for flight in flight_listings:
        try:
            # 2. Extract Type (Cheapest, 3rd Fastest, Free Meal)
            # This is located in the top badge area
            badge_area = flight.find('div', class_='absolute -top-2 left-20')
            flight_offer = None
            if badge_area:
                text_badge = badge_area.find('span')
                if text_badge:
                    flight_offer = text_badge.get_text(strip=True)

            # Extract Airline Name and Flight Number
            airlineInfo = flight.find('div',class_='airlineInfo')
            if airlineInfo:
                airlineFlightDetails = airlineInfo.find_all('p')
                airline = airlineFlightDetails[0].get_text(strip=True)
                flight_no = airlineFlightDetails[1].get_text(strip=True)
            
             
            # Times are usually in <h6> tags, locations in <p class="body-sm text-secondary">
            times = flight.find_all('h6', class_='h6 text-primary font-medium')
            dep_time = times[0].text.strip()
            arr_time = times[1].text.strip()
            
            timeTile = flight.find("div",class_="timeTile")
            if timeTile:
                locations = timeTile.find_all('p' )
                departure_city = locations[0].text.strip()
                duration = locations[1].text.strip()
                flight_type =  locations[2].text.strip() # non-stop, 1 stop or multiple
                arrival_city = locations[3].text.strip()
                 
            # Extract Price section data
            price_section = flight.find("div",class_="text-right")
            price = None
            offers = None
            if price_section:
                price = price_section.find('div',{'class':'items-baseline'}).text.strip()
                offers = price_section.find('span',{'class':'dynot'}).text.strip()

            badge_area = flight.find('div', class_='absolute -top-2 left-20')
            flight_type = "Standard"
            if badge_area:
                # Check for text badges
                text_badge = badge_area.find('span')
                if text_badge:
                    flight_type = text_badge.get_text(strip=True)

            layover_duration = None
            layover_city = None
            flights_data.append({
                 'Airline': airline,
                 'flight_no': flight_no,
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
                    'extra_badges':flight_offer,
                    'source': 'ixigo'
            })
        except Exception as e:
             logger.info(f"Error processing flight: {e}")
             raise e
    #print(f"\nExtraction complete: {len(flights_data)} flights extracted from {index}")        
    return flights_data

def save_to_csv(data, filename):
    """Saves the extracted data to a CSV file."""
    if not data:
        logger.info("No data to save.")
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


def parse_flight_data(uniquas):
    """Main function to run the script."""
    flight_data = []
    html_file_path = [HTML_FILE_PATH_IXIGO.format(unqiuas=f"{uniquas}_{i}") for i in range(0, 8000,1000)]
    for i in html_file_path:
        try:
            with open(i, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            logger.info(f"Error: The file '{i}' was not found.")
            logger.info("Please ensure the script is in the same directory as 'mmt_res.html'.")
            return
        except Exception as e:
            logger.info(f"Error reading file: {e}")
            return

        flight_data.extend(extract_flight_data(html_content,i))
    flight_data = [dict(fs) for fs in set(frozenset(d.items()) for d in flight_data)]
    logger.info(flight_data)
    return flight_data
   # save_to_csv(flight_data, OUTPUT_CSV_PATH)


if __name__ == "__main__":
    parse_flight_data()