from flask import Flask, request, abort, g
import json
from redis import Redis

from datetime import datetime
from forecast import get_forecast

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

@app.route("/getforecast", methods=["GET"])
def forecast_EP():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    height = request.args.get("height")

    if lat is None:
        lat = 55.675806
    if lon is None:
        lon = 12.510884
    if height is None:
        height = 5

    curr_hour = datetime.now().strftime("%Y-%m-%d-%H")

    cache_key = "{}-{}-{}-{}".format(lat, lon, height, curr_hour)

    red = get_redis()
    res = red.get(cache_key)
    if res is not None: res = json.loads(res)

    if res is None:
        res = get_forecast(lat, lon, height)
        if res is None: abort(500)
        red.set(cache_key, json.dumps(res))

    res = json.dumps({"success": True, "result": res})

    return res, 200, {"ContentType": "application/json"}
    
