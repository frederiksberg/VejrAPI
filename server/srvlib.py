import RSA
import os
import base64
import json
from pslib import check_connection, add_hourly, add_daily

def insert_example(example, Creds):
    t = example["type"]
    
    if t == "hourly":
        return add_hourly(Creds.username, Creds.passwd, example)
    elif t == "daily":
        return add_daily(Creds.username, Creds.passwd, example)
    else:
        return None
    

class Creds:
    __slots__ = ["username", "passwd"]
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd

class Auth:
    def __init__(self):
        self.Sessions = {}

    def parse_req(self ,req):
        req = req.encode("ascii")
        clear_req = RSA.decrypt(req)
        clear_req = clear_req.decode("ascii")
        try:
            dict_req = json.loads(clear_req)
        except:
            print("Failed JSON parse")
            return None
        
        if not "username" in dict_req or not "passwd" in dict_req or not "pub_key" in dict_req:
            print("Dict malformed")
            return None # Dict malformed

        # Check if is valid login
        user = dict_req["username"]
        pwd = dict_req["passwd"]
        pub_key = dict_req["pub_key"]
        pub_key = pub_key.encode("ascii")
        pub_key = base64.b64decode(pub_key)

        if not check_connection(user, pwd):
            print("Failed user/pwd verification", "{}:{}".format(user, pwd), "{}:{}".format(type(user), type(pwd)))
            return None

        token = self.new_session(user, pwd)
        print(token)
        token = token.encode("ascii")
        token = RSA.encrypt_with_key(token, pub_key)
        return token

    def validate_token(self, q):
        try:
            q = q.encode("ascii")
            q = RSA.decrypt(q)
            q = q.decode("ascii")

            d = json.loads(q)

            obs = d["obs"]
            token = d["token"]

            if token in self.Sessions:
                return self.Sessions[token], obs
        except:
            return None
            
    def new_session(self, username, passwd):
        # Generate a new token
        while True:
            token = base64.b64encode(os.urandom(32)).decode("ascii")
            # Check for key collisions
            if not token in self.Sessions: break

        self.Sessions[token] = Creds(username, passwd)
        return token