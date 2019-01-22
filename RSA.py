import os.path
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

def BuildKey():
    '''Build a new RSA key pair
    
    Raises:
        OSError -- If purge_keys return False, ie. we weren't able to dispath of previous keys.
    '''

    if not purge_keys():
        raise OSError("Was unable to delete previous key files.\nCheck access rights.")

    new_key = RSA.generate(4096)

    private_key = new_key.exportKey("PEM")
    public_key = new_key.publickey().exportKey("PEM")

    with open("rsa", "wb") as fp:
        fp.write(private_key)

    with open("rsa.pub", "wb") as fp:
        fp.write(public_key)

def key_exists():
    '''Checks if either key file exists.
    
    Returns:
        bool -- True if either key exists
    '''

    if os.path.isfile("rsa") and os.path.isfile("rsa.pub"):
        return True
    else:
        return False

def purge_keys():
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
    

def get_public_key(b64=True):
    '''Get's servers RSA public key as a raw string.
    
    Returns:
        str -- Public key string
    '''

    if not key_exists():
        BuildKey()
    
    with open("rsa.pub", "rb") as fp:
        return fp.read()
    
def encrypt(data):
    '''Encrypts data using servers public key.
    This is what a clients encryption method should look like.
    
    Arguments:
        data {bytes} -- A bytestring of data
    
    Returns:
        bytes -- Returns base64 encoded bytestring of encrypted data
    '''

    assert isinstance(data, bytes)

    key_data = get_public_key(b64=False)
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

def decrypt(data):
    '''Decrypts base64 encoded data using the servers private key.
    
    Arguments:
        data {bytes} -- base64 encoded bytestring
    
    Returns:
        bytes -- Cleartext bytestring with leading and trailing spaces stripped
    '''

    assert isinstance(data, bytes)

    if not key_exists():
        BuildKey()

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
