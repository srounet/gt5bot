import logging
import time

from optparse import OptionParser

from gt5bot.bot import Bot


def bspec_bot():
    """Bspec script for CLI usage."""
    usage = "usage: %prog [options] psn_id psn_password"
    parser = OptionParser(usage=usage)
    parser.add_option('--silent', action='store_true', dest='silent', default=False, help='Disable/enable verbose.')
    parser.add_option('--limit', dest='limit', help='Limit the bot to N races.')
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        parser.error('psn_id and psn_password are required.')

    logging.basicConfig(format='%(asctime)s %(message)s')
    logger = logging.getLogger('gt5bot')
    logger.setLevel(logging.INFO)

    if options.silent:
        logger.info = null_log

    psn_id, psn_pw = args[0:2]
    bot = Bot(psn_id, psn_pw)
    logger.info('Authenticate')
    if not bot.authenticate():
        logger.info('Bad login or password.')
        exit()
    while True:
        logger.info('== Starting a new race ==')
        logger.info('Get races')
        # @todo: GET FRIEND LIST
        #friends = bot.get_friend_list()

        races = bot.race_ids

        logger.debug('Set race to: %s' % races[0])
        event = bot.set_race(races[0])

        logger.debug('Get %s driver list' % bot.profile['id'])
        my_drivers = bot.driver_list(bot.profile['id'])

        # @todo: GET A FRIEND DRIVER LIST / OR MORE
        #logger.debug('Get %s driver list' % friend_name)
        #friend_drivers = bot.driver_list(friend_name)

        logger.debug('Add entry: %s' % my_drivers[0]['driver_id'])
        bot.add_driver(bot.profile['id'], my_drivers[0]['driver_id'])

        # @todo: ADD FRIEND DRIVER
        #logger.info('Add entry: %s' % friend_drivers[0]['driver_id'])
        #bot.add_driver(friend_name, friend_drivers[0]['driver_id'])

        logger.info('Go race !')
        bot.start_race()

        # XXX: TRACK ENDING INSTEAD OF SLEEP
        logger.info('Sleep 30 minutes')
        time.sleep(60*30)


def null_log(msg, *args, **kwargs):
    pass
