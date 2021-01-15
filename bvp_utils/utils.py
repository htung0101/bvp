import os
import re
import socket
import getpass
import yaml




def get_query_dir(query_dir):
    hostname = socket.gethostname()
    username = getpass.getuser()
    paths_yaml_fn = os.path.join(get_source_dir(), 'paths.yaml')
    with open(paths_yaml_fn, 'r') as f: 
        paths_config = yaml.load(f, Loader=yaml.Loader)

    for hostname_re in paths_config:
        if re.compile(hostname_re).match(hostname) is not None:
            for username_re in paths_config[hostname_re]:
                if re.compile(username_re).match(username) is not None:
                    return paths_config[hostname_re][username_re][query_dir]

    raise Exception('No matching hostname or username in config file')

def get_hostname():
    hostname = socket.gethostname()
    return hostname

def get_markdata_dir():
    return get_query_dir('markdata_dir')


def get_source_dir():
    return os.getenv("BVP_SOURCE_DIR")
