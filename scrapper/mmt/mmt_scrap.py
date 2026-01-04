from seleniumbase import SB
import logging,sys,random,string
from scrapper.scrap_config import HTML_FILE_PATH_MMT
# --- Configure Logging to use STDERR ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
  
# --- Configuration ---

def scrap_sb(origin="LKO", destination="IXL", travel_date="18/11/2025"):
    with SB(uc=True, test=True) as sb:
        url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{travel_date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng"
        sb.activate_cdp_mode(url)
        
        sb.sleep(9)
        sb.click('button.priceLockProCtaButton.whiteText')
        sb.get_page_source()
        #sb.save_screenshot('./ss/mmt_res.png', full_page=True)
        sr = sb.get_page_source()
        rand_choice = random.choice(string.ascii_lowercase)

        with open(f"./scrapper/mmt_res_{rand_choice}.html", "w", encoding="utf-8") as f:
            f.write(sr)
        logger.info("MMT Scraping completed")
        sb.quit()
def scrap_data(origin, destination, travel_date,random_string):
    """Synchronous scraping function to run in thread"""
    logger.info(f"Scraping MMT for {origin} to {destination} on {travel_date}")
    try:
        with SB(uc=True, test=True, xvfb=True) as sb:
            url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{travel_date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng"
            sb.activate_cdp_mode(url)
            
            sb.sleep(5)
            try:
                sb.click('button.priceLockProCtaButton.whiteText')
            except Exception:
                logger.warning("Popup button not found or already closed.")
                
            sr = sb.get_page_source()
            
            import os
            os.makedirs(os.path.dirname(HTML_FILE_PATH_MMT), exist_ok=True)
            
            html_file =  HTML_FILE_PATH_MMT.format(unqiuas=random_string) #unqiuas
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(sr)
            logger.info("Scraping completed successfully.")
            sb.quit()
            return html_file
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise e

if __name__ == "__main__":
    scrap_sb()