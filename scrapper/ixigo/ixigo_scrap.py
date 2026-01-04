from seleniumbase import SB
import logging
import sys
from scrapper.scrap_config import HTML_FILE_PATH_IXIGO
from scrapper.mmt.mmt_scrap import scrap_sb
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
def scrap_data(origin="LKO", destination="DEL", travel_date="25122025",uniquas=None):
    '''
    Format for mmt: travel_date="18/11/2025"
    Format for ixigo: travel_date=15122025
    '''
    #with SB(uc=True, test=True, headless2=True) as sb:
    try:
        logger.info(f"Scraping ixigo for {origin} to {destination} on {travel_date}")
        with SB(uc=True, test=True) as sb:    
            #url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{travel_date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng"
            url = f"https://www.ixigo.com/search/result/flight?from={origin}&to={destination}&date={travel_date}&adults=1&children=0&infants=0&class=e&source=Search+Form"
            sb.set_window_size(1400, 8000)

            sb.activate_cdp_mode(url)
            sb.activate_jquery()
            sb.sleep(12)
            #document.elementFromPoint(2, 5).click();
            sb.execute_script("jQuery, document.elementFromPoint(2, 5).click();")
            
            sb.sleep(2)
            for i in range(0, 8000,1000):
                sb.execute_script(f"document.querySelector('.bg-neutral-60.h-screen.overflow-y-auto').scrollTo(0, {i});")
                #sb.save_screenshot('./ss/mmt_res.png')
                sr = sb.get_page_source()
                #sr = sb.get_attribute(".listingContainer div","innerHTML")
                write_to_file(sr,filename=HTML_FILE_PATH_IXIGO.format(unqiuas=f"{uniquas}_{i}"),mode="w")
                
            print("Scraping ixigo completed")
            sb.quit()
    except Exception as e:
        logger.error(f"Error in ixigo scraping: {e}")
        
def write_to_file(content, filename="./scrapper/mmt_res.html",mode="a"):
    with open(filename, mode, encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    scrap_sb()