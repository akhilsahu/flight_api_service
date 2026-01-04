from scrapper.mmt import mmt_scrap
from scrapper.mmt import data_extraction as mmt_data_extraction
import random,string,time,uuid
 
def execute(origin, destination, travel_date):
    rand_choice = f"{time.time()}"
    mmt_scrap.scrap_data(origin, destination, travel_date,rand_choice) 
    parsing_data = mmt_data_extraction.parse_flight_data(rand_choice)
    return parsing_data