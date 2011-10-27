import logging
import time

from optparse import OptionParser

from gt5bot.bot import Bot


def bspec_bot():
    """Bspec script for CLI usage."""
    usage = "usage: %prog [options] psn_id psn_password"
    parser = OptionParser(usage=usage)
    parser.add_option('--silent', dest='silent', default=False, help='Disable/enable verbose.')
    parser.add_option('--limit', dest='limit', help='Limit the bot to N races.')
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        parser.error('psn_id and psn_password are required.')
