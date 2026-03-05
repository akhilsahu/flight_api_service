from utils.config  import INSTANT_SCRAPPER_REGISTRY
import os,json,redis
from datetime import datetime
from tasks.flight_scrape_task import source_flight_mapping
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))

def get_instant_scrapper(from_iata, to_iata, formatted_date, task_id):
    for scr_config,config in INSTANT_SCRAPPER_REGISTRY.items():
          print(f"scr_config.............: {scr_config}, config: {config}")
          date_obj = datetime.strptime(formatted_date, "%Y-%m-%d")
          formatted_date = date_obj.strftime(config["dateFormat"])
          results = config["func"](from_iata, to_iata, formatted_date)
          cache_key = f"{task_id}:{scr_config}:{from_iata}:{to_iata}:{formatted_date}"
          r.set(cache_key, json.dumps(results))
    final_collection = source_flight_mapping([results]) 
    r.set(f"{task_id}", json.dumps(final_collection))
    #print(f"results.............: {results}")
    return final_collection

if __name__ == "__main__":
     get_instant_scrapper("DEL", "BOM", "03/03/2026", "1234567890")


