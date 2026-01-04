import csv
from bs4 import BeautifulSoup
import re
import logging
import sys
from scrapper.scrap_config import HTML_FILE_PATH_MMT
#from scrap_config import HTML_FILE_PATH_MMT
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)

# --- Common MMT Selector Clues (Adjust these based on your specific HTML) ---
# 1. Main container for a single flight listing
FLIGHT_CARD_SELECTOR = 'div[class*="clusterContent"]'

FLIGHT_LISTING_SELECTOR = 'div[data-test*=component-clusterItem]'
# 2. Selector for the Airline Name
AIRLINE_SELECTOR = 'p[class*="airlineName"]'
AIRLINE_CODE_SELECTOR = 'p[class*="fliCode"]'
# 3. Selector for Departure/Arrival Time (often grouped with city)
TIME_CITY_GROUP_SELECTOR = 'p[class*="flightTimeInfo"]'
# 4. Selector for Flight Duration (often in the center)
START_DURATION_SELECTOR = 'div[class*="timeInfoLeft"]'
LAYOVER_DURATION_SELECTOR = 'div[class*="stop-info"]'
END_DURATION_SELECTOR = 'div[class*="timeInfoRight"]'
# 5. Selector for the Final Price
PRICE_SELECTOR = 'div[class*="priceSection"]'

def write_html_to_file(html_content, filename="./scrapper/ss/mmt1_pretty.html"):
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

    # Find all flight listing cards
    flight_cards = soup.select(FLIGHT_LISTING_SELECTOR)
 
    if not flight_cards:
        #print(f"Warning: No flight cards found using selector: {FLIGHT_LISTING_SELECTOR}")
        logger.info("Please inspect the HTML to find the correct selector for a single flight block.")
        return []

    #print(f"Found {len(flight_cards)} potential flight listings. Extracting data...")

    for flight_card in flight_cards:
        try:
            # 1. Extract Airline Name
            airline_element = flight_card.select_one(AIRLINE_SELECTOR)
            airline = airline_element.text.strip() if airline_element else "N/A"

            airline_code_element = flight_card.select_one(AIRLINE_CODE_SELECTOR)
            airline_code = airline_code_element.text.strip() if airline_code_element else "N/A"

            # 2. Extract Time and City information (Departure and Arrival)
            time_city_groups = flight_card.select(TIME_CITY_GROUP_SELECTOR)
            
            # Assuming the first group is Departure and the last is Arrival
            if len(time_city_groups) >= 2:
                # Extracting Departure Time and City
                dep_time = time_city_groups[0].text.strip()  #time_city_groups[0].find('p', class_='flightTimeInfo').text.strip() if time_city_groups[0].find('p', class_='timeInfo__time') else 'N/A'
                #dep_city = time_city_groups[0].find('p', class_='flightTimeInfo').text.strip() if time_city_groups[0].find('p', class_='timeInfo__city') else 'N/A'
                
                # Extracting Arrival Time and City
                arr_time = time_city_groups[-1].text.strip()#time_city_groups[-1].find('p', class_='timeInfo__time').text.strip() if time_city_groups[-1].find('p', class_='timeInfo__time') else 'N/A'
                #arr_city = time_city_groups[-1].find('p', class_='timeInfo__city').text.strip() if time_city_groups[-1].find('p', class_='timeInfo__city') else 'N/A'
            else:
                # Fallback if the structure is unexpected
                dep_time, dep_city, arr_time, arr_city = 'N/A', 'N/A', 'N/A', 'N/A'


            # 3. Extract Duration
            departure_element = flight_card.select_one(START_DURATION_SELECTOR)
            departure_time = departure_element.find('p').text if departure_element.find('p') else "N/A"
            departure_city= departure_element.find('p',class_ = 'blackText').text
            
            layover_element = flight_card.select_one(LAYOVER_DURATION_SELECTOR)
            layover_duration = layover_element.find('p').text if layover_element.find('p') else "N/A"
            layover_city = layover_element.find('p',class_ = 'flightsLayoverInfo').text
            

            arrival_element = flight_card.select_one(END_DURATION_SELECTOR)
            arrival_time = arrival_element.find('p').text if arrival_element.find('p') else "N/A"
            arrival_city = arrival_element.find('p',class_ = 'blackText').text

            # 4. Extract Price
            price_element = flight_card.select_one(PRICE_SELECTOR)

            raw_price = price_element.find("span").text.strip() if price_element else "N/A"
            # Clean up the price string (remove currency symbol, commas)
            #price = re.sub(r'[^\d]', '', raw_price) if raw_price != "N/A" else raw_price
            offers = flight_card.find("p",class_="alertMsg appendBottom10 appendTop10 textCenter").text

            flight_data.append({
                'Airline': airline,
                "flight_no": airline_code,
                'Departure_Time': departure_time,
                'Departure_City': departure_city,
                'Arrival_Time': arrival_time,
                'Arrival_City': arrival_city,
                'Layover_Duration': layover_duration,
                'Layover_City': layover_city,
                'Arrival_City': arrival_city,
                'Price': raw_price,
                'Offers': offers,
                'source': 'mmt'
            })

        except Exception as e:
            logger.error(f"Skipping a flight card due to error: {e}")
            continue

    return flight_data

def save_to_csv(data, filename):
    """Saves the extracted data to a CSV file."""
    if not data:
        logger.error("No data to save.")
        return

    fieldnames = list(data[0].keys())
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"\nSuccessfully extracted {len(data)} flights and saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")


def parse_flight_data(unquas_file_code):
    """Main function to run the script."""
    try:
        html_file_path = HTML_FILE_PATH_MMT.format(unqiuas=unquas_file_code)
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        logger.error(f"Error: The file '{html_file_path}' was not found.")
        logger.error("Please ensure the script is in the same directory as 'mmt_res.html'.")
        return
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return

    flight_data = extract_flight_data(html_content)
    return flight_data
    #save_to_csv(flight_data, OUTPUT_CSV_PATH)


# if __name__ == "__main__":

#     unquas_file_code
#     parse_flight_data()