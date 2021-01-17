import os
import re
import socket
import getpass
#import yaml

import argparse
import sys
import ipdb
st=ipdb.set_trace

def get_query_dir(query_dir):
    hostname = socket.gethostname()
    username = getpass.getuser()
    paths_yaml_fn = os.path.join(get_source_dir(), 'paths.yaml')
    paths_config = dict()
    with open(paths_yaml_fn, 'r') as f:
        for line in f:
            if line[0] is not " ": # top name
                hostname = line.strip()[:-1]
                paths_config[hostname] = dict()
            elif line[4] is not " ":
                user_name = line.strip()[:-1]
                paths_config[hostname][user_name] = dict()
            else:

                if line.strip().startswith("#"):
                    continue
                item, path = line.strip().split(":")
                item = item.strip()
                path = path.strip()
                paths_config[hostname][user_name][item] = path
            if line.strip() == "":
                continue
        #paths_config = yaml.load(f, Loader=yaml.Loader)

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

def get_quantized_dir():
    return get_query_dir('quantized_dir')

def get_source_dir():
    return os.getenv("BVP_SOURCE_DIR")

class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self._get_argv_after_doubledash())