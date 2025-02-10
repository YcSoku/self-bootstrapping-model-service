import hashlib

def generate_md5(input_string):
    
    md5_hasher = hashlib.md5()
    
    md5_hasher.update(input_string.encode('utf-8'))
    
    md5_hash = md5_hasher.hexdigest()
    
    return md5_hash
