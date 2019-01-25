from flask import Flask, request, abort
import json

import RSA
import srvlib
from forecast import get_forecast

app = Flask(__name__)

auth = srvlib.Auth()

@app.route("/auth", methods=["GET", "POST"])
def start_session():
    if request.method == "GET":
        return RSA.get_public_key()
    elif request.method == "POST":
        req = request.form["req"]
        token = auth.parse_req(req)
        if not token:
            abort(403)
        return token

@app.route("/insert", methods=["GET", "POST"])
def insert():
    if request.method == "POST":
        q = request.form["q"]

        ret = auth.validate_token(q)
        if not ret:
            abort(403)
        
        cred, obs = ret

        if srvlib.insert_example(obs, cred) is None:
            abort(400)

        return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
    else:
        abort(404)

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

    res = get_forecast(lat, lon, height)

    if res is None:
        abort(500)

    res = json.dumps({"success": True, "result": res})

    return res, 200, {"ContentType": "application/json"}
    