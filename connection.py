from configobj import ConfigObj
import os
import sys

def get_connection(con_name='default'):
    if not con_name:
        con_name = 'default'
    
    # Link to our config
    c = os.path.expanduser('~/.mf.conf')

    # Do we have a config
    if os.path.exists(c):

        # Parse our config
        config = ConfigObj(c)    
        for sect in config.sections:
            if sect.startswith('connection:'):
                try:
                    assert config[sect].has_key('user'), \
                        "Missing 'user' setting in %s (%s)." % (_file, sect)
                    assert config[sect].has_key('api_key'), \
                        "Missing 'api_key' setting in %s (%s)." % (_file, sect)
                    assert config[sect].has_key('url'), \
                        "Missing 'url' setting in %s (%s)." % (_file, sect)    
                except AssertionError, e:
                    raise e
                    
                name = sect.split(':')[1]
                if name == con_name:
                    api = {}
                    api['api_key'] = config[sect]['api_key']
                    api['user'] = config[sect]['user']
                    api['url'] = config[sect]['url']
                    return (api)
    else:
        return False
