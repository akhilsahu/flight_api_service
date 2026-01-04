from collections import defaultdict
import redis
import json
import os
from worker import celery_app
from scrapper.mmt import scrap_extract as mmt
from scrapper.ixigo import scrap_extract as ixigo
from celery.utils.log import get_task_logger
from utils.config import SCRAPPER_REGISTRY

from datetime import datetime
r = redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))
logger = get_task_logger(__name__)
def broadcast(task_id, msg, progress, results=None, done=False, source=None, is_stale=False):
    logger.info(f"[{source.upper() if source else 'SYSTEM'}] {msg}")
    payload = {
        "status": msg,
        "progress": progress,
        "done": done,
        "source": source,
        "is_stale": is_stale
    }
    if results:
        payload["results"] = results
    r.publish(task_id, json.dumps(payload))


@celery_app.task(name='merge_results')
def merge_results(all_source_data, from_iata, to_iata, travel_date_iso, task_id):
    """
    all_source_data: [[{mmt_f1}, {mmt_f2}], [{ixigo_f1}]]
    This task 'clubs' everything into a single collection.
    """
    logger.info(f"Merging all sources for {from_iata}->{to_iata}")

    # 1. Your Aim: Clubbing logic
    # Structure: { "AI101": { "mmt": [...], "ixigo": [...] } }
    flight_data_dict = defaultdict(lambda: defaultdict(list))

    for source_list in all_source_data:
        if not source_list:
            continue
            
        for flight in source_list:
            f_no = str(flight.get('flight_no', '')).replace(" ", "").upper()
            src = flight.get('source')
            
            if f_no and src:
                flight_data_dict[f_no][src].append(flight)

    # 2. Convert to standard dict for JSON compatibility
    final_collection = {k: dict(v) for k, v in flight_data_dict.items()}

    # 3. Update the Shared Redis Cache Key
    # This key now represents the 'Collection of All Sources'
    cache_key = f"flights:{from_iata}:{to_iata}:{travel_date_iso}"
    r.set(cache_key, json.dumps(final_collection))
    
    # 4. Broadcast the 'TOTAL' collection to the UI
    broadcast(
        task_id, 
        msg="All sources clubbed into master collection", 
        progress=100, 
        results=final_collection, 
        done=True, 
        source="TOTAL"
    )
    
    return final_collection

@celery_app.task(bind=True, name='execute_single_source_scrape')
def execute_single_source_scrape(self, source_name, from_iata, to_iata, travel_date_iso, task_id):
    if source_name not in SCRAPPER_REGISTRY:
        return
    
    scr_config = SCRAPPER_REGISTRY[source_name]
    cache_key = f"flights:{from_iata}:{to_iata}:{travel_date_iso}"
    logger.info(f"Source Func: {scr_config['func']}" )
    try:
        # 1. Convert ISO (2026-01-02) to Source Format (e.g. 02/01/2026)
        date_obj = datetime.strptime(travel_date_iso, "%Y-%m-%d")
        formatted_date = date_obj.strftime(scr_config["dateFormat"])
        broadcast(task_id, f"Searching {source_name.upper()}...", 20, source=source_name)

        # 2. Execute the scraper function from registry
        results = scr_config["func"](from_iata, to_iata, formatted_date)

        # 3. Permanent Cache Update (No TTL)
        r.set(cache_key, json.dumps(results))
    
        # 4. Final Broadcast of Fresh Data
        broadcast(task_id, f"{source_name.upper()} Complete ", 80, 
                  results=results, done=False, source=source_name, is_stale=False)

        return results
    except Exception as e:
        broadcast(task_id, f"{source_name} Error: {str(e)}", 0, done=True, source=source_name)
        return []


@celery_app.task(bind=True, name='execute_flight_scrape')
def execute_flight_scrape(self, from_iata, to_iata, travel_date, task_id):

    broadcast("Launching Browser...", 10)
    final_data = {"results": []} # Initialize with default
    cache_key = f"flights:{from_iata}:{to_iata}:{travel_date}"
    try:
        # Ensure these are strings before passing to scraper
        results = mmt.execute(str(from_iata), str(to_iata), str(travel_date))
        
        broadcast("Data extracted successfully", 90)
        final_data = {"results": results}
        # 1. Overwrite the Redis store (No expiration/TTL so it never dies)
        r.set(cache_key, json.dumps(results)) 
        # 2. Broadcast the fresh results to the UI
        r.publish(task_id, json.dumps({
            "status": "Updated with latest prices",
            "progress": 100,
            "done": True,
            "results": results,
            "is_stale": False
        }))
        broadcast("Complete", 100, done=True)
        
        return final_data

    except Exception as e:
        error_msg = str(e)
        broadcast(f"Error: {error_msg}", 0, done=True)
        return {"error": error_msg, "results": []}