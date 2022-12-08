from .load.load_site_min import load_site_min
from .load.load_site_hour import load_site_hour

def site(trange=['2015-01-01', '2015-01-02'], res='min', site='kak'):
    ###
    if res == 'min' :
        load_site_min(trange,site=site)

    if res == 'hour' :
        load_site_hour(trange,site=site)

    return True
