from seleniumbase import SB
import logging,sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
def scrap_data(origin="LKO", destination="DEL", travel_date="02/01/2026"):
    '''
    Format for mmt: travel_date="18/11/2025"
    Format for ixigo: travel_date=15122025
    Format for expedia: travel_date=02/01/2026
    '''
    #with SB(uc=True, test=True, headless2=True) as sb:
    logger.info(f"Scraping Expedia for {origin} to {destination} on {travel_date}")
    try:
        with SB(uc=True, test=True) as sb:    
            #url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{travel_date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng"
            url = f"https://www.expedia.co.in/Flights-Search?flight-type=on&mode=search&trip=oneway&leg1=from:%20({origin}),to:%20({destination}),departure:{travel_date}TANYT,fromType:U,toType:AIRPORT&options=cabinclass:economy&fromDate=02/01/2026&d1=2026-1-2&passengers=adults:1,infantinlap:N"
            #url = f"https://www.ixigo.com/search/result/flight?from={origin}&to={destination}&date={travel_date}&adults=1&children=0&infants=0&class=e&source=Search+Form"
            sb.set_window_size(1400, 8000)

            sb.activate_cdp_mode(url)
            sb.activate_jquery()
            sb.sleep(12)
            
            sb.sleep(2)
            
            sr = sb.get_page_source()
            sr = sb.get_attribute("#app-flights-shopping-pwa div","innerHTML")
            write_to_file(sr,filename=f"./scrapper/ss/mmt_res_expedia.html",mode="w")
            print("Scraping completed")
            sb.quit()
    except Exception as e:
        print(e)

def write_to_file(content, filename="./scrapper/mmt_res.html",mode="a"):
    with open(filename, mode, encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    scrap_data()