#!/usr/bin/env python
"""
----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <srounet@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return Fabien Reboia.
----------------------------------------------------------------------------
"""

from datetime import datetime, timedelta
from functools import wraps

from gt5bot import api


REMOTE_STATUS = [
    'Please prepare to Remote Race.',
    'You are now ready to start a Remote Race.',
    'Currently taking part in Remote Race...',
    'View XXXXX\'s race results.',
    'Remote Race',
]


class InvalidStatus(Exception):
    def __init__(self, status_ids, remote_status_id):
        self.status_ids = status_ids
        self.remote_status_id = remote_status_id
    def __str__(self):
        required_status_ids = ', '.join(self.status_ids)
        msg = "Required status ids are: %s, actual status id is: %s."
        return msg % (required_status_ids, self.remote_status_id)


class NotAuthenticated(Exception):
    def __str__(self):
        return "Not authenticated with playstation network."


class BadDriverCount(Exception):
    def __init__(self, driver_count):
        self.driver_count
    def __str__(self):
        return "Two driver are required, %s active driver(s)" % self.driver_count


class NoRaceSelected(Exception): pass
class InvalidClassName(Exception): pass


def login_required(func):
    """Test if active user is connected to psn.
    Raise if not connected, otherwise it just call the decorated function
    and return its result.

    Keyword arguments:
    func  --  a <Bot> method.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], Bot):
            raise InvalidClassName
        if not args[0].is_loggued:
            raise NotAuthenticated
        return func(*args, **kwargs)
    return wrapper


def race_required(func):
    """Test if we have an active race.
    Raise if <Bot>.<set_race> has not been called yet.

    Keyword arguments:
    func  --  a <Bot> method.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], Bot):
            raise InvalidClassName
        if not args[0].active_race:
            raise NoRaceSelected
        return func(*args, **kwargs)
    return wrapper


def drivers_required(func):
    """Test if there are at least two drivers for the active race.
    Raise if <Bot>.<add_driver> has not been called twice with different
    drivers yet.

    Keyword arguments:
    func  --  a <Bot> method.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], Bot):
            raise InvalidClassName
        if not len(args[0].drivers) >= 2:
            raise BadDriverCount(len(args[0].drivers))
        return func(*args, **kwargs)
    return wrapper


def status(status_ids):
    """Test if remoterace status match in status_ids.
    Raise if status did not match.

    Keyword arguments:
    status_ids  -- a list of status id.
    """
    def wrapper(func):
        def _wrapper(*args, **kwargs):
            if not isinstance(args[0], Bot):
                raise InvalidClassName
            status = args[0].status
            remote_status_id = int(status['status'])
            if remote_status_id in status_ids:
                return func(*args, **kwargs)
            raise InvalidStatus(status_ids, remote_status_id)
        return _wrapper
    return wrapper


class Bot(object):
    def __init__(self, psn_username, psn_password):
        """Class wrapper for gran turismo 5 bspec api.

        Keyword arguments:
        psn_username  -- playstation network account username
        psn_password  -- playstation network account password
        """
        self.psn_username = psn_username
        self.psn_password = psn_password
        self.is_loggued = False
        self.profile = {}
        self.races = []
        self.active_race = None
        self.drivers = []
        self._last_updated_status = datetime.now() - timedelta(minutes=1)
        self._cached_status = None

    def authenticate(self):
        """Establish a connection to the playstation network in order to obtain
        the SSO cookie.
        """
        try:
            api.authenticate(self.psn_username, self.psn_password)
        except api.AuthenticationError:
            self.is_loggued = False
        else:
            self.is_loggued = True
            self.update_profile()
        return self.is_loggued

    @login_required
    def update_profile(self):
        """Fetch gran turismo remoterace to obtain some profile informations.
        Calling this method update the self.profile var.
        """
        self.profile = api.get_raw_profile()
        return self.profile

    @property
    @login_required
    def race_ids(self):
        """Fetch gran turismo remoterace to obtain available race ids.
        Calling this method update the self.races var.
        """
        self.races = api.get_race(self.profile['id'])
        return self.races

    @login_required
    @status([1])
    @race_required
    def driver_list(self, online_id):
        """Fetch player (online_id) available drivers for active race.

        Keyword arguments:
        online_id   -- a playstation network id
        """
        drivers = api.get_driver_list(online_id)
        return drivers

    @login_required
    @status([1])
    def set_race(self, race_id):
        """Define race_id as the active race.

        Keyword arguments:
        race_id  -- identify the race number
        """
        api.set_race(self.profile['id'], race_id)
        self.active_race = race_id

    @login_required
    @status([1])
    @race_required
    def add_driver(self, online_id, driver_id):
        """Add a driver to the active race.

        Keyword arguments:
        online_id   -- a playstation network id
        driver_id   -- a driver id
        """
        api.add_entry(online_id, driver_id)
        self.drivers.append(driver_id)

    @login_required
    @status([1])
    @race_required
    @drivers_required
    def start_race(self):
        """Start the race with selected race and drivers."""
        api.go_race()
        self.race = None
        self.drivers = []

    @property
    @login_required
    def status(self):
        """Return remoterace status."""
        updated_difference = self._last_updated_status + timedelta(minutes=1)
        if datetime.now() > updated_difference:
            self._last_updated_status = datetime.now()
            self._cached_status = api.get_status()
        return self._cached_status
