#!/usr/bin/env python
"""
----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <srounet@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return Fabien Reboia
 * ----------------------------------------------------------------------------
"""

import urllib2


class Browser(object):
    """A wrapper around http web requests."""

    def __init__(self):
        """Nothing special, we just need the standard urlib2 opener here."""
        self.opener = self._build_opener()

    def fetch(self, url, data=None, headers=None):
        """Make an http request and return the response.
        Will raise and urllib2.URLError if something bad happend.

        Keyword arguments:
        url     -- target url
        data    -- an urlencoded list of values to post
        headers -- a list of key/values to be send as header
        """
        request = self._build_request(url, data=data, headers=headers)
        try:
            response = self.opener.open(request)
        except urllib2.URLError as err:
            err.opener = self.opener
            err.request = request
            raise
        return response

    def _build_opener(self):
        """Create a standard opener for classic web requests."""
        opener = urllib2.build_opener()
        return opener

    def _build_request(self, url, data=None, headers=None):
        """Create an urllib2 Request with headers informations if set.

        Keyword arguments:
        url     -- target url
        data    -- an urlencoded list of values to post
        headers -- a list of key/values to be send as header
        """
        request = urllib2.Request(url, data, headers or {})
        return request


class BrowserWithCookies(Browser):
    """A C{Browser} that maintains cookies between requests.

    Session information can thus be updated and sent to the destination from
    request to request.
    """
    def _build_opener(self):
        """Append a cookie processor to the opener."""
        opener = Browser._build_opener(self)
        opener.add_handler(urllib2.HTTPCookieProcessor())
        return opener

default_browser = Browser()


def install_browser(browser):
    """For an easy usage, we use a global default_browser in order to
    provide a unique Browser object for all of our requests.

    Keyword arguments:
    browser     -- The browser to be set as default.
    """
    global default_browser
    if not isinstance(browser, Browser):
        raise InvalidBrowserError('invalid browser:', browser)
    default_browser = browser


class InvalidBrowserError(Exception):
    pass
