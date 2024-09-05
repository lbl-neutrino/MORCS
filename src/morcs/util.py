from fabric import Connection

def connect_krbrs( host ):
    connect_kwargs = {'gss_auth': True, 'gss_kex': True}

    return Connection(host, connect_kwargs = connect_kwargs)

