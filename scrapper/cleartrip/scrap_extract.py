from scrapper.cleartrip import cleartrip_scrap
from scrapper.cleartrip import data_extraction  
import random,string,time,uuid
 
def execute(origin, destination, travel_date):
    rand_choice = time.time()
    data = cleartrip_scrap.scrap_data(origin, destination, travel_date,rand_choice) 
    parsing_data = data_extraction.parse_flight_data(data,rand_choice)
    return parsing_data

if __name__ == "__main__":
    execute("LKO", "DEL", "25/03/2026")