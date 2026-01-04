from re import search
from flask import Blueprint, request, jsonify
from urllib3 import response
from google_places_comprende import search_nearest_airports_from_city,get_airport_suggestions
autocomplete_bp = Blueprint('autocomplete', __name__)

@autocomplete_bp.route('/api/autocomplete/')
def search_city():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    results = search_nearest_airports_from_city(query)
    response= jsonify(results)
    return response

@autocomplete_bp.route('/api/autocomplete/airport')
def search_airport_name():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    results = get_airport_suggestions(query)
    
    response= jsonify(results)
    
    return response

@autocomplete_bp.route('/api/healthy/')
def healthy():
    return "Health Check"
