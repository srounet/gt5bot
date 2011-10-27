#!/usr/bin/env python
"""
----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <srounet@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return Fabien Reboia.
----------------------------------------------------------------------------
"""

import re

try:
    import json
except ImportError:
    import simplejson as json

from urllib import urlencode
from gt5bot import navigator


DOMAIN = 'https://us.gran-turismo.com/us'

API = {
    'GO_HOME': DOMAIN + '/gt5/user/',
    'GET_PROFILE': DOMAIN + '/api/gt5/profile/?online_id={online_id}',
    'GET_RACE': DOMAIN + '/gt5/user/{online_id}/remoterace/',
    'RESET': DOMAIN + '/api/gt5/remoterace/?job=0',
    'GET_CARLIST': DOMAIN + '/api/gt5/remoterace/?job=1&online_id={online_id}',
    'GET_DRIVERLIST': DOMAIN + '/api/gt5/remoterace/?job=2&online_id={online_id}',
    'ADD_ENTRY': DOMAIN + '/api/gt5/remoterace/?job=3',
    'REMOVE_ENTRY': DOMAIN + '/api/gt5/remoterace/?job=4',
    'SELECT_EVENT': DOMAIN + '/api/gt5/remoterace/?job=5',
    'GET_STATUS': DOMAIN + '/api/gt5/remoterace/?job=6',
    'GO_RACE': DOMAIN + '/api/gt5/remoterace/?job=7',
    'GET_MONITORLIST': DOMAIN + '/api/gt5/remoterace/?job=8',
    'GET_RESULTLIST': DOMAIN + '/api/gt5/remoterace/?job=9',
    'GET_RESULT': DOMAIN + '/api/gt5/remoterace/?job=10',
    'GET_ENTRYLIST': DOMAIN + '/api/gt5/remoterace/?job=11',
    'END_RACE': DOMAIN + '/api/gt5/remoterace/?job=12',
    'SET_RACE': DOMAIN + '/gt5/user/{online_id}/remoterace/',
}


class AuthenticationError(Exception):
    pass


def authenticate(psn_username, psn_password):
    """
    Single Sign On to playstation in order to obtain a cookie and then access
    the gt5 API. Raise AuthenticationError if could not signin.

    Keyword arguments:
    psn_username  -- playstation network account username
    psn_password  -- playstation network account password
    """
    sso_url = 'https://store.playstation.com/j_acegi_external_security_check?target=/external/login.action'
    params = urlencode({
        'j_username': psn_username,
        'j_password': psn_password,
        'returnURL': DOMAIN + '/signin/index.do',
    })
    response = navigator.fetch(sso_url, params)
    content = response.read()
    if '<title>' in content:
        raise AuthenticationError
    m = re.search(r'''sessionId=(?P<session>.*?)&''', content)
    if not m:
        raise AuthenticationError
    session_id = m.groupdict()['session']
    cookie_url = DOMAIN + '/signin/signin.do?sessionId=%s' % session_id
    navigator.fetch(cookie_url)


def get_raw_profile():
    """Crunch home page, to obtain profile informations such as psn_id.

    Return profile as a json dict.
    """
    response = navigator.fetch(API['GO_HOME'])
    content = response.read()
    m = re.search(r'''target_profile = '(?P<profile>.*?)'.evalJSON''', content)
    if not m:
        return
    raw_profile = m.groupdict()['profile']
    profile = json.loads(raw_profile)
    return profile


def get_profile(online_id):
    """ Return a profile from its online_id.

    Keyword arguments:
    online_id   -- a playstation network id
    """
    profile_url = API['GET_PROFILE'].format(**{
        'online_id': online_id,
    })
    response = navigator.fetch(profile_url)
    content = response.read()
    # ???
    return content


def get_driver_list(online_id):
    """Return an array of available drivers for selected race.

    Keyword arguments:
    online_id   -- a playstation network id
    """
    remote_status_url = API['GET_DRIVERLIST'].format(**{
        'online_id': online_id,
    })
    response = navigator.fetch(remote_status_url)
    content = response.read()
    status = json.loads(content)
    return status


def set_race(online_id, article_id):
    """Select a race from an article_id.

    Keyword arguments:
    online_id   -- a playstation network id
    article_id  -- an article id (in fact it should be named race id)
    """
    set_race_url = API['SET_RACE'].format(**{
        'online_id': online_id,
    })
    params = urlencode({
        'article_id': article_id,
    })
    response = navigator.fetch(set_race_url, params)
    content = response.read()
    return content


def add_entry(online_id, driver_id):
    """Add a driver to the selected race event.

    Keyword arguments:
    online_id   -- a playstation network id
    driver_id   -- a driver id
    """
    params = urlencode({
        'online_id': online_id,
        'driver_id': driver_id,
    })
    response = navigator.fetch(API['ADD_ENTRY'], params)
    content = response.read()
    return content


def remove_entry(driver_id):
    """Remove a driver from the selected race event.

    Keyword arguments:
    driver_id   -- a driver id
    """
    params = urlencode({
        'driver_id': driver_id
    })
    response = navigator.fetch(API['REMOVE_ENTRY'], params)
    content = response.read()
    return content


def get_race(online_id):
    """Return a list of article ids. Each article id correspond to a race.

    Keyword arguments:
    online_id   -- a playstation network id
    article_id  -- an article id (in fact it should be named race id)
    """
    race_url = API['GET_RACE'].format(**{
        'online_id': online_id,
    })
    response = navigator.fetch(race_url)
    content = response.read()
    races = re.findall("gt5bspec.selectEvent\((?P<article_id>.*?)\)", content)
    return races


def get_car_list(online_id, article_id):
    """Add a driver to the selected race event.

    Keyword arguments:
    online_id   -- a playstation network id
    article_id  -- an article id (in fact it should be named race id)
    """
    content = set_race(online_id, article_id)
    car_list = re.findall(r"""_list.push\("(?P<car_name>.*?)\);""", content)
    return car_list


def get_entry_list():
    """Return the list of all selected drivers for the current race event."""
    response = navigator.fetch(API['GET_ENTRYLIST'])
    content = response.read()
    json_data = json.loads(content)
    return json_data


def go_race():
    """Launch the race, on selected article_id with registered drivers."""
    response = navigator.fetch(API['GO_RACE'])
    content = response.read()
    json_data = json.loads(content)
    return json_data


def get_status():
    """Return remoterace status."""
    response = navigator.fetch(API['GET_STATUS'])
    content = response.read()
    json_data = json.loads(content)
    return json_data
