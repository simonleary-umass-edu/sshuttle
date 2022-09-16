import os
import re

"""
given a name, look through ssh configs for hostname, port, user
the name is case sensitive
looks through /etc/ssh/ssh_config, ~/.ssh/config, and ~/.ssh/config.d/*
configs overwrite each other in the above order, config.d is sorted
configs must be utf-8
Anything specified for 'Host *' is ignored

TODO includes
"""

def get_config_file_names():
    """
    /etc/ssh/ssh_config, ~/.ssh/config, and ~/.ssh/config.d/*, whatever exists
    """
    ssh_dir = os.path.expanduser('~') + "/.ssh/"
    config_file_names = [
        "/etc/ssh/ssh_config",
        ssh_dir + "config"
    ]
    extra_configs_dir = ssh_dir + "config.d/"
    if os.path.isdir(extra_configs_dir):
        for extra_config in sorted(os.listdir(extra_configs_dir)):
            config_file_names.append(extra_configs_dir + extra_config)
    # make sure they all exist and are not directories
    config_file_names = [ x for x in config_file_names if os.path.isfile(x)]
    return config_file_names

def parse_file(filename, name):
    config = {
    "hostname": "",
    "port": "",
    "user": ""
    }
    with open(filename, encoding="utf-8") as config_file:
        config_file_contents = config_file.read()
    # is this config file relevant?
    if name not in config_file_contents:
        return None        
    # replace tabs with spaces
    config_file_contents.replace('\t', "    ")
    # make lines
    config_file_lines = config_file_contents.splitlines()
    # strip lines
    config_file_lines = [ x.strip() for x in config_file_lines]
    # remove empty lines
    config_file_lines = [ x for x in config_file_lines if x]
    # remove comments
    config_file_lines = [ x for x in config_file_lines if x[0] != '#']
    
    # scan down the lines, if you find Host {name} then 
    # look for port/hostname/user in the following lines
    # until you see Host {something else}
    line_is_relevant = False
    for line in config_file_lines:
        if re.search(fr'^(H|h)ost\s+', line):
            # if this is the start of the config for the name we want
            if re.search(fr'^(H|h)ost\s+{name}$', line):
                line_is_relevant = True
                continue
            # if this is the start of the config for some other name
            line_is_relevant = False
            continue
        if not line_is_relevant:
            continue
        try:
            hostname = re.search(r'^(H|h)ost(N|n)ame\s+(.+)$', line).group(3)
            config["hostname"] = hostname
        except AttributeError:
            pass
        try:
            port = re.search(r'^(P|p)ort\s+(.+)$', line).group(2)
            config["port"] = port
        except AttributeError:
            pass
        try:
            user = re.search(r'^(U|u)ser\s+(.+)$', line).group(2)
            config["user"] = user
        except AttributeError:
            pass
        
    return config

def get_config(name):
    config = {
    "hostname": "",
    "port": "",
    "user": ""
    }
    config_file_names = get_config_file_names()
    if not config_file_names:
        return None
    for config_file_name in config_file_names:
        config_found = parse_file(config_file_name, name)
        if not config_found:
            continue
        # write the found config into the existing config dict
        config = config | config_found
        print(config) # deleteme?
    return config
    # todo print when there are configs other than name port user
    # suggest user add key to agent

if __name__=="__main__":
    get_config("bingus")
