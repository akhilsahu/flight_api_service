from scrapper.ixigo import ixigo_scrap
from scrapper.ixigo import data_extraction  
import random,string,time,uuid
 
def execute(origin, destination, travel_date):
    rand_choice = time.time()
    ixigo_scrap.scrap_data(origin, destination, travel_date,rand_choice) 
    parsing_data = data_extraction.parse_flight_data(rand_choice)
    return parsing_data