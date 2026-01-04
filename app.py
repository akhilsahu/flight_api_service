from flask import Flask
from flask_cors import CORS
from tasks.utils import make_celery
import os 
import redis

 
app = Flask(__name__)

# 1. Define the config
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# 2. Assign it to the app.config dictionary
app.config["CELERY_CONFIG"] = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
}

# 2. Create Celery Instance
celery = make_celery(app)
r = redis.from_url(REDIS_URL)

from api.autocomplete import autocomplete_bp
from api.flights import flight_api_bp

CORS(app) # 1. This adds the header
@app.after_request
def after_request(response):
   # response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.set("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.set("ngrok-skip-browser-warning", "true")
    return response

app.register_blueprint(autocomplete_bp)
app.register_blueprint(flight_api_bp)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"