 
import logging,requests,sys,json
from scrapper.scrap_config import HTML_FILE_PATH_CLEARTRIP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
def scrap_data(origin="LKO", destination="DEL", travel_date="25/03/2026",uniquas=None):
    '''
    Format for mmt: travel_date="18/11/2025"
    Format for ixigo: travel_date=15122025
    Format for cleartrip: travel_date=25/03/2026

    '''
    #with SB(uc=True, test=True, headless2=True) as sb:
    logger.info(f"Scraping ct for {origin} to {destination} on {travel_date}")
    """
    Fetches flight data using user-friendly parameter names.
    Automatically formats dates if provided as 'DDMMYYYY'.
    """
    url = "https://www.cleartrip.com/flight/search/v2"
    
    # Handle the date formatting if it's passed as '25122025'
    formatted_date = travel_date
    if len(travel_date) == 8 and travel_date.isdigit():
        formatted_date = f"{travel_date[:2]}/{travel_date[2:4]}/{travel_date[4:]}"

    # Mapping your function parameters to Cleartrip's internal keys
    params = {
        "from": origin,
        "source_header": origin,
        "to": destination,
        "destination_header": destination,
        "depart_date": formatted_date,
        "class": "Economy",
        "adults": "1",
        "childs": "0",
        "infants": "0",
        "mobileApp": "true",
        "intl": "n",
        "responseType": "jsonV3",
        "source": "DESKTOP",
        "utm_currency": "INR",
        "sft": "",
        "return_date": "",
        "carrier": "",
        "cfw": "false",
        "multiFare": "true",
        "isFFSC": "true",
        "filter_version": "v2"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.cleartrip.com/flights/results",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        print(f"Requesting: {origin} -> {destination} on {formatted_date}")
        response = requests.get(url, params=params, headers=headers)
        print(f"Response: {response.status_code},{response.url}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            data = response.json()
            # Basic check to see if we got flight data back
            write_to_file(json.dumps(data),filename=HTML_FILE_PATH_CLEARTRIP.format(unqiuas=uniquas),mode="w")
            if 'solutions' in data:
                print(f"Success! Found {len(data['solutions'])} flight options.")
            return data
            
             
        else:
            print(f"Failed. Status: {response.status_code}")
             
        
    except Exception as e:
        print(f"Error in cleartrip scraping: {e}")
        return None

def write_to_file(content, filename="./scrapper/mmt_res.html",mode="a"):
    with open(filename, mode, encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    scrap_data()