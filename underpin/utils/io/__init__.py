import yaml

def read(f):
    with open(f):
        return yaml.safe_load_all(f)
    
def write(data, f):
     with open(f, 'w'):
        return yaml.safe_dump_all(f)