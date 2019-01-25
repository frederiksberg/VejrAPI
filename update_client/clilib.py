import os.path
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from configparser import ConfigParser
import requests

_URL = "http://localhost:5000"

# region RSA

def _BuildKey():
    '''Build a new RSA key pair
    
    Raises:
        OSError -- If purge_keys return False, ie. we weren't able to dispath of previous keys.
    '''

    if not _purge_keys():
        raise OSError("Was unable to delete previous key files.\nCheck access rights.")

    new_key = RSA.generate(4096)

    private_key = new_key.exportKey("PEM")
    public_key = new_key.publickey().exportKey("PEM")

    with open("rsa", "wb") as fp:
        fp.write(private_key)

    with open("rsa.pub", "wb") as fp:
        fp.write(public_key)

def _key_exists():
    '''Checks if either key file exists.
    
    Returns:
        bool -- True if either key exists
    '''

    if os.path.isfile("rsa") and os.path.isfile("rsa.pub"):
        return True
    else:
        return False

def _purge_keys():
    '''Purges key files
    
    Returns:
        bool -- Returns True if success, False otherwise
    '''

    try:
        if os.path.isfile("rsa"):
            os.remove("rsa")
        if os.path.isfile("rsa.pub"):
            os.remove("rsa.pub")
    except OSError:
        return False
    return True

def _get_public_key(b64=True):
    '''Get's clients RSA public key as a raw string.
    
    Returns:
        str -- Public key string
    '''

    if not _key_exists():
        _BuildKey()
    
    with open("rsa.pub", "rb") as fp:
        data =  fp.read()
    if b64:
        return base64.b64encode(data)
    else:
        return data

def _encrypt(data):
    '''Encrypts data using clients private key.
    
    Arguments:
        data {bytes} -- A bytestring of data
    
    Returns:
        bytes -- Returns base64 encoded bytestring of encrypted data
    '''

    assert isinstance(data, bytes)

    if not _key_exists():
        _BuildKey()

    with open("rsa", "rb") as fp:
        key_data = fp.read()
    assert key_data

    rsa_key = RSA.importKey(key_data)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    chunk_size = 470 # (4096/8) - 42
    offset = 0
    end_loop = False
    encrypted = b""

    while not end_loop:
        chunk = data[offset:offset + chunk_size]

        if len(chunk) % chunk_size != 0:
            # We are processing last chunk; end and pad
            end_loop = True
            chunk += b" " * (chunk_size - len(chunk))
        
        encrypted += rsa_key.encrypt(chunk)

        offset += chunk_size
    
    return base64.b64encode(encrypted)

def _decrypt(data):
    '''Decrypts base64 encoded data using the clients private key.
    
    Arguments:
        data {bytes} -- base64 encoded bytestring
    
    Returns:
        bytes -- Cleartext bytestring with leading and trailing spaces stripped
    '''

    assert isinstance(data, bytes)

    if not _key_exists():
        _BuildKey()

    with open("rsa", "rb") as fp:
        key_data = fp.read()
    assert key_data

    rsa_key = RSA.importKey(key_data)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    data = base64.b64decode(data)

    chunk_size = 512 # 4096 / 8
    offset = 0
    decrypted = b""

    while offset < len(data):
        chunk = data[offset:offset + chunk_size]
        decrypted += rsa_key.decrypt(chunk)
        offset += chunk_size

    return decrypted.strip()

def _encrypt_with_key(data, key):
    '''Like encrypt, but allows specification of a key.
    
    Arguments:
        data {bytes} -- Data to be decrypted
        key_file {string} -- Key file location. Can be either public or private.
    
    Returns:
        bytes -- Decrypted data
    '''
    assert isinstance(data, bytes)

    rsa_key = RSA.importKey(key)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    chunk_size = 470 # (4096/8) - 42
    offset = 0
    end_loop = False
    encrypted = b""

    while not end_loop:
        chunk = data[offset:offset + chunk_size]

        if len(chunk) % chunk_size != 0:
            # We are processing last chunk; end and pad
            end_loop = True
            chunk += b" " * (chunk_size - len(chunk))
        
        encrypted += rsa_key.encrypt(chunk)

        offset += chunk_size
    
    return base64.b64encode(encrypted)

# endregion

class daily_example:
    def __init__(self, date,
                       temperature_mean, temperature_min, temperature_max, 
                       pressure_mean, pressure_min, pressure_max, 
                       windspd_mean, windspd_min, windspd_max,
                       humidity_mean, humidity_min, humidity_max,
                       precipitation):
        self.date = date
        self.temperature_mean = temperature_mean
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max
        self.pressure_mean = pressure_mean
        self.pressure_min = pressure_min
        self.pressure_max = pressure_max
        self.windspd_mean = windspd_mean
        self.windspd_min = windspd_min
        self.windspd_max = windspd_max
        self.humidity_mean = humidity_mean
        self.humidity_min = humidity_min
        self.humidity_max = humidity_max
        self.precipitation = precipitation

    def asdict(self):
        return {
            "type": "daily",
            "from_date": self.date,
            "temperature_mean": self.temperature_mean,
            "temperature_min": self.temperature_min,
            "temperature_max": self.temperature_max,
            "pressure_mean": self.pressure_mean,
            "pressure_min": self.pressure_min,
            "pressure_max": self.pressure_max,
            "windspd_mean": self.windspd_mean,
            "windspd_min": self.windspd_min,
            "windspd_max": self.windspd_max,
            "humidity_mean": self.humidity_mean,
            "humidity_min": self.humidity_min,
            "humidity_max": self.humidity_max,
            "precipitation": self.precipitation
        }

class hourly_example:
    def __init__(self, date,
                       temperature, pressure,
                       windspd, humidity,
                       precipitation):
        self.date = date
        self.temperature = temperature
        self.pressure = pressure
        self.windspd = windspd
        self.humidity = humidity
        self.precipitation = precipitation

    def asdict(self):
        return {
            "type": "hourly",
            "from_date" : self.date,
            "temperature" : self.temperature,
            "pressure" : self.pressure,
            "windspd" : self.windspd,
            "humidity" : self.humidity,
            "precipitation" : self.precipitation
        }

def _send_example(example, token, pub_key):
    
    data = {
        "obs": example.asdict(),
        "token": token
    }

    data = json.dumps(data, separators=(",",":"))
    data = data.encode("ascii")
    data = _encrypt_with_key(data, pub_key)
    data = data.decode("ascii")

    resp = requests.post(_URL + "/insert", data={"q": data})

    if resp.status_code != 200:
        raise ValueError("Server refused; Status code: {}".format(resp.status_code))

def send_examples(examples):
    assert isinstance(examples, list)

    # Auth
    token, pub_key = _authenticate()

    for ex in examples:
        _send_example(ex, token, pub_key)


def _config(filename="psql.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
        return db

def _authenticate():
    params = _config()
    if not params:
        raise FileNotFoundError("Can't find psql.ini")    

    msg = {}
    msg["username"] = params["user"]
    msg["passwd"] = params["pwd"]
    msg["pub_key"] = _get_public_key().decode("ascii")

    msg_json = json.dumps(msg, separators=(",", ":"))

    # Ask for servers public key
    resp = requests.get(_URL + "/auth")
    if resp.status_code != 200:
        raise ValueError("Server said no; Status code: {}".format(resp.status_code))

    srv_pub_key = resp.text
    srv_pub_key = srv_pub_key.encode("ascii")
    srv_pub_key = base64.b64decode(srv_pub_key)
    
    # Encrypt our request with server public key
    msg_json = msg_json.encode("ascii")
    msg_enc = _encrypt_with_key(msg_json, srv_pub_key)

    # Send auth request
    resp = requests.post(_URL + "/auth", data={
        "req": msg_enc
    })

    if resp.status_code != 200:
        raise ValueError("Server said no; Status code: {}".format(resp.status_code))

    token = resp.text

    token = token.encode("ascii")
    token = _decrypt(token)

    # make python string
    token = token.decode("ascii")

    return token, srv_pub_key



