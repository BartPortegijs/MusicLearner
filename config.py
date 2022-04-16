import configparser

config_path = "configfile.ini"

def read_config(configfile):
    config_obj = configparser.ConfigParser()
    config_obj.read(configfile)
    
    client_id = config_obj.get('connection','client_id')
    secret_id = config_obj['connection']['secret_id']
    uri = config_obj['connection']['uri']
    scope = config_obj['connection']['scope']
    return {'client_id': client_id, 'secret_id':secret_id, 
            'scope':scope, 'uri':uri}

if __name__ == "__main__":
    configuration_dict = {'client_id': '...',
    'secret_id': '...',
    'scope': 'playlist-read-private playlist-read-private playlist-modify-private user-read-recently-played',
    'uri': 'http://127.0.0.1:9000/'}

    config = configparser.ConfigParser()
    config.add_section('connection')

    for key,value in configuration_dict.items():
        config.set('connection', key, value)

    with open(f"configfile.ini", 'w') as configfile:
        config.write(configfile)