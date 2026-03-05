from scrapper.mmt import mmt_scrap
from scrapper.mmt import data_extraction as mmt_data_extraction
import random,string,time,uuid
 
def execute(origin, destination, travel_date):
    rand_choice = f"{time.time()}"
    mmt_scrap.scrap_data(origin, destination, travel_date,rand_choice) 
    parsing_data = mmt_data_extraction.read_parse_flight_files(rand_choice)
    return parsing_data