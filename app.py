import RSA
import os
import base64
import json
from flask import Flask, request

class Creds:
    __slots__ = ["username", "passwd"]
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd

Sessions = {}

app = Flask(__name__)

@app.route("/auth", methods=["GET", "POST"])
def start_session():
    if request.method == "GET":
        return RSA.get_public_key()
    elif request.method == "POST":
        req = request.form["req"]
        token = parse_req(req)
        return token


def parse_req(req):
    req = req.encode("ascii")
    clear_req = RSA.decrypt(req)
    dict_req = json.loads(clear_req)
    if not "username" in dict_req or not "passwd" in dict_req:
        raise ValueError("Input malformed") # TODO: Handle this gracefully
    token = new_session(dict_req["username"], dict_req["passwd"])
    return token

def validate_token(token):
    if token in Sessions:
        return Sessions[token]
        
def new_session(username, passwd):
    # Generate a new token
    while True:
        token = base64.b64encode(os.urandom(32)).decode("ascii")
        # Check for key collisions
        if not token in Sessions: break
    
    Sessions[token] = Creds(username, passwd)
    return token