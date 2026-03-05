from seleniumbase import SB
import logging,sys,random,string,time

try:
    from scrapper.scrap_config import HTML_FILE_PATH_MMT, HTML_FILE_BASE_PATH_MMT
except ImportError:
    HTML_FILE_BASE_PATH_MMT = "./scrapper/ss/mmt/{unqiuas}/"
    HTML_FILE_PATH_MMT = "./scrapper/ss/mmt/{unqiuas}/mmt_res_{unqiuas}_{num}.html"

# --- Configure Logging to use STDERR ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr 
)
logger = logging.getLogger(__name__)
  
# --- Configuration ---

def scrap_sb(origin="LKO", destination="DEL", travel_date="05/02/2026"):
    with SB(uc=True, test=True) as sb:
        url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{travel_date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng"
        sb.activate_cdp_mode(url)
        
        sb.sleep(9)
        try:

           sb.click('button.priceLockProCtaButton.whiteText')
        except Exception:
            logger.warning("Popup button not found or already closed.")

        sb.get_page_source()
        #sb.save_screenshot('./ss/mmt_res.png', full_page=True)
        sr = sb.get_page_source()
        rand_choice = random.choice(string.ascii_lowercase)
        file_name = f"./scrapper/mmt_res_{rand_choice}.html"
        with open(f"./scrapper/mmt_res_{rand_choice}.html", "w", encoding="utf-8") as f:
            f.write(sr)
        logger.info("MMT Scraping completed")
        sb.quit()

def write_to_file(content, filename="./scrapper/mmt_res.html",mode="a"):
    with open(filename, mode, encoding="utf-8") as f:
            f.write(content)

def scroll_to_end(sb,random_string):
   scroll_step = 600  # Pixels to scroll each step
   pause_time = 1.0   # Seconds to wait for segment loading

   current_position = 0
   sr = sb.get_page_source()

   html_file = HTML_FILE_PATH_MMT.format(unqiuas=random_string,num=1)
      
   write_to_file(sr, filename=html_file, mode="w")
   while True:
        # Get current total height (it may grow if new content loads)
        sr = sb.get_page_source()
        html_file = HTML_FILE_PATH_MMT.format(unqiuas=random_string,num=current_position)
        write_to_file(sr, filename=html_file, mode="w")

        total_height = sb.execute_script("return document.body.scrollHeight")
        # Scroll down by one step
        sb.execute_script(f"window.scrollBy(0, {scroll_step});")
        # sr = sb.get_page_source()    
        # write_to_file(sr, filename=html_file, mode="w")
        
        current_position += scroll_step
        time.sleep(pause_time)
        
        # Break if we have scrolled past the end of the current content
        if current_position >= total_height:
            # Final check: see if height grew after the last scroll
            new_total_height = sb.execute_script("return document.body.scrollHeight")
            if new_total_height == total_height:
                break
        


def scrap_data(origin="LKO", destination="DEL", travel_date="05/02/2026",random_string=None):

    """Synchronous scraping function to run in thread
        origin: string - iata code of the origin city
        destination: string - iata code of the destination city
        travel_date: string - date of the travel in dd/mm/yyyy format
        random_string: string - random string to be used as the unique identifier for the scraper
    
    """
    
    
    logger.info(f"Scraping MMT for {origin} to {destination} on {travel_date}")
    if random_string is None:
        random_string = f"{time.time()}"
    try:
        with SB(uc=True, test=True, xvfb=False) as sb:
            url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{travel_date}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&lang=eng"
            sb.activate_cdp_mode(url)
            
            sb.sleep(5)
            try:
                sb.click('button.priceLockProCtaButton.whiteText')
            except Exception:
                logger.warning("Popup button not found or already closed.")
            
            #sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
            
            html_path =  HTML_FILE_BASE_PATH_MMT.format(unqiuas=random_string) #unqiuas
            import os
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            logger.info(f"Saving HTML PATH to {html_path}")
            scroll_to_end(sb,random_string)
            #for i in range(0, 8000,1000):
            
            #sb.execute_script(f"window.scrollTo(0, {i});")

            # with open(html_file, "w", encoding="utf-8") as f:
            #     f.write(sr)

            logger.info("Scraping completed successfully.")
            sb.quit()
            #return html_file
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise e

if __name__ == "__main__":
    scrap_data()