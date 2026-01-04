import json
from re import search
from flask import Blueprint, Response, request, jsonify
from urllib3 import response
from scrapper.mmt import scrap_extract as mmt
from utils import  format_date
from tasks.flight_scrape_task import execute_flight_scrape,execute_single_source_scrape,merge_results
import redis
import uuid
from utils import config as app_config
from celery import group,chord
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


flight_api_bp = Blueprint('flight', __name__)

@flight_api_bp.route('/api/flight/')
def flight_search():
    from_iata = request.args.get('from', '')
    to_iata = request.args.get('to', '')
    travel_date = request.args.get('travel_date', '')
    date_obj =  format_date.convert_to_date_std(travel_date)
    key = "mmt"
    registry = app_config.SCRAPPER_REGISTRY
    date_str = date_obj.strftime(registry[key]["dateFormat"])
    if not from_iata and not to_iata and not travel_date:
        return jsonify([])
    results = mmt.execute(from_iata,to_iata,date_str)
    response= jsonify(results)
    return response

import os
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))

@flight_api_bp.route('/api/flight/start')
def flight_search_start():
    task_id = str(uuid.uuid4())
    origin, dest = request.args.get('from'), request.args.get('to') 
    travel_date = request.args.get('travel_date', 'YYYY-MM-DD') 
    cache_key = f"flights:{origin}:{dest}:{travel_date}"
    # Check if we have "stale" data to show immediately
    stale_data = r.get(cache_key)
    if stale_data:
        r.publish(task_id, json.dumps({
            "status": "Showing cached prices (updating live...)",
            "progress": 5,
            "results": json.loads(stale_data),
            "is_stale": True
        }))
    # Triggering the background stuff from the tasks dir
    active_sources = list(app_config.SCRAPPER_REGISTRY.keys())

    # 2. Parallel Header (Individual Scrapers)
    header = [
        execute_single_source_scrape.s(s, origin, dest, travel_date, task_id) 
        for s in active_sources
    ]
    
    # 3. Callback (The Collector/Clubber)
    # The result of the header is passed as the first argument automatically
    callback = merge_results.s(origin, dest, travel_date, task_id)
    
    # 4. Fire the Chord
    chord_result = chord(header)(callback)
    # job = group([
    #     execute_single_source_scrape.s(s, origin, dest, travel_date, task_id) 
    #     for s in active_sources
    # ])
    # job.apply_async()
    # execute_flight_scrape.apply_async(
    #     args=[request.args.get('from'), request.args.get('to'), date_str, task_id],
    #     task_id=task_id
    # )
    
    return jsonify({"task_id": task_id, "stream_url": f"/api/flight/stream/{task_id}"})

@flight_api_bp.route('/api/flight/stream/<task_id>')
def stream_results(task_id):
    def event_stream():
        pubsub = r.pubsub()
        pubsub.subscribe(task_id)
        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data_str = message['data'].decode('utf-8')
                    yield f"data: {data_str}\n\n" 
                    import json
                    data_json = json.loads(data_str) 

                    # Check if the worker sent the done signal
                    if data_json.get("done") is True:
                        # 1. Send an explicit backend-closed message
                        final_msg = json.dumps({
                            "status": "Stream closed by backend", 
                            "progress": 100, 
                            "done": True,
                            "event": "CLOSE"
                        })
                        yield f"data: {final_msg}\n\n"
                        #break 
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # 2. Clean up Redis resources
            pubsub.unsubscribe(task_id)
            pubsub.close()
            
    return Response(event_stream(), mimetype="text/event-stream")

@flight_api_bp.route('/api/flight/healthy/')
def healthy():
    return "Health Check Flight"
