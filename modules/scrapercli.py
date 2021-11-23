#!/usr/bin/env python
#
# File: $Id: scrape_cli.py 2014 2009-10-21 08:21:58Z scanner $
#
"""
A simple CLI interface to our python scraper module.
"""

# system imports
#
import sys
import os
import optparse
import readline

import logging
import logging.handlers

#
import scraper

##################################################################
##################################################################
#
class ResultSet(object):
    """
    The result set object holds on to a bunch of results from previous
    queries so that successive queries can drill in to the results of
    previous queries.
    """

    ##################################################################
    #
    def __init__(self):
        self.lookup_results = []

    ##################################################################
    #
    def output(self):
        """
        return the result set information as a nicely formatted
        string.
        """
        if len(self.lookup_results) > 0:
            print "Lookup results:"
            for i,lr in enumerate(self.lookup_results):
                print "%02d: %s" % (i+1,lr.title)

############################################################################
#
def setup_option_parser():
    """
    Very simple option parser object.
    """
    parser = optparse.OptionParser(usage = "%prog [options]",
                                   version = "%prog 0.1")
    parser.add_option("--scraper", action="store", type="string",
                      dest="scraper",
                      default = None,
                      help = "The file containing the XML scraper definition "
                      "to use.")
    return parser

##################################################################
##################################################################
#
class CommandProcessor(object):
    """
    A class that holds together all the bits and pieces for handling
    commands that poke stuff and return results based on the results
    of our XML scraper definition.
    """

    ##################################################################
    #
    def __init__(self, scraper_definition_file, logger = logging.getLogger()):
        """
        """
        f = open(scraper_definition_file, 'r')
        xml = f.read()
        f.close()
        self.scraper = scraper.Scraper(xml, logger)

    ##################################################################
    #
    def cmd_settings(self):
        """
        Display the current settings of the scraper.
        """
        # Print out any settings that the scraper may have.
        #
        for sid in self.scraper.settings.ids:
            print "Setting: %s(%s): %s" % \
                (self.scraper.settings.labels[sid], sid,
                 self.scraper.settings.values[sid])

    ##################################################################
    #
    def cmd_set_setting(self, setting_id, value):
        """
        Set a given setting to a given value. IF you try to set a setting that
        does not exist we give you an error.
        Arguments:
        - `setting_id`: The setting to set.
        - `value`: The value to set it to.
        """
        try:
            self.scraper.settings.set_value(setting_id, value)
        except KeyError:
            print "There is no such setting '%s'." % setting_id
            print "Valid settings are: %s" % ", ".join(self.scraper.settings.ids)
        return

    ####################################################################
    #
    def cmd_lookup(self, query_str, result_set):
        """
        Take the given 'query_str' and see what shows match it.
        we expect back a list of possible show match objects.
        We append these to the list of show match objects on the result_set.
        Arguments:
        - `query_str`:
        - `result_set`:
        """
        results = self.scraper.lookup(query_str)
        if len(results) > 0:
            print "Found %d results for query '%s'" % (len(results), query_str)
            for i,r in enumerate(results):
                print "%02d: %s" % (i+1, r.title.encode('ascii',
                                                        'xmlcharrefreplace'))
            result_set.lookup_results = results
        return result_set

    ##################################################################
    #
    def cmd_details(self, show, result_set):
        """
        Get the details for the given lookup results.
        Arguments:
        - `show`: a lookup results item.
        """
        show.get_details()
        print "Details for '%s'" % show.title.encode('ascii',
                                                     'xmlcharrefreplace')
        print "%s\n" % str(show)

        result_set.details = show
        return result_set

    ##################################################################
    #
    def cmd_episode_list(self, show):
        """
        Get the episode list for a tv show.
        Arguments:
        - `show`: A TVShowDetails object for which we are
                  going to get its episode list.
        """
        if not isinstance(show, scraper.Series):
            raise TypeError("%s is not a Series." % repr(show))
        
        episodes = show.get_episode_list()
        if len(episodes) == 0:
            print "No episode..."
            return
        for i,ep in enumerate(episodes):
            print "%02d Episode: %s" % (i+1, str(ep))

    ##################################################################
    #
    def cmd_episode_details(self, ep):
        """
        Arguments:
        - `episode`: Episode to get the extended details for.
        """
        ep.get_details()
        print "Episode: %s" % str(ep)
        print "  Plot: %s" % ep.plot.encode('ascii','xmlcharrefreplace')
        print "  Aired: %s" % ep.aired
        if ep.director:
            print "  Director: %s" % ep.director.encode('ascii','xmlcharrefreplace')
        print "  Rating: %s" % ep.rating
        if ep.thumbnail:
            print "  Thumbnail url: %s" % ep.thumbnail
        if len(ep.credits) > 0:
            print "  Credits:"
            for credit in ep.credits:
                print "    %s" % credit.encode('ascii','xmlcharrefreplace')
        if len(ep.actors) > 0:
            print "  Actors:"
            for actor in ep.actors:
                print "    %s" % actor.encode('ascii','xmlcharrefreplace')

        return ep

#############################################################################
#
def main():
    """
    Main loop. Initialize readline and then enter a loop reading and
    acting on the user's input.
    """

    # Read our history file for readline, if it exists.
    #
    histfile = os.path.join(os.environ["HOME"], ".scrape_cli_hist")
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass

    # Parse command line options. Kinda obvious..
    #
    parser = setup_option_parser()
    (options, args) = parser.parse_args()

    # XXX our verbose debugging logger.
    #
    logger = logging.getLogger("scrape_cli")
    logger.setLevel(logging.DEBUG)
#     ch = logging.StreamHandler()
    ch = logging.handlers.RotatingFileHandler("/tmp/scrape_cli.log")
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # The command processor is what actually runs all of our commands. It is
    # tied to a specific scraper.
    #
    cp = CommandProcessor(options.scraper, logger)

    # Print out the current settings..
    #
    cp.cmd_settings()

    # We have a result state object that is used to hold the results
    # of various commands. This way successive commands can operate on the
    # results of previous commands.
    #
    result_set = ResultSet()

    # The main loop. We need some sort of state so that we can do
    # successive drilldowns in to data we look up.
    #
    while True:
        try:
            query = raw_input("scrape> ").strip()
            logger.debug("executing command: '%s'" % query)
        except EOFError:
            readline.write_history_file(histfile)
            print "\n"
            return

        if len(query) == 0:
            continue

        (command, sep, rem) = query.partition(" ")
        rem = rem.strip()

        # Now operate on the command... we pass along the remainder of the
        # query and the current result set object so that the command can
        # operate on the result of previous queries.
        #
        if command == "lookup":
            result_set = cp.cmd_lookup(rem, result_set)
        elif command == "details":
            try:
                which = int(rem) - 1
            except ValueError:
                print "** '%s' must be the number of the lookup result you " \
                    "want to look up details for. It must be an integer." % rem
                continue

            num_lookup_results = len(result_set.lookup_results)
            if which < 0 or which > (num_lookup_results - 1):
                print "** The lookup result index must be between 1 and " \
                    "%d" % num_lookup_results
                continue
            lr = result_set.lookup_results[which]
            print "Looking up details for: '%s'" % lr.title.encode('ascii', 'xmlcharrefreplace')
            result_set = cp.cmd_details(lr, result_set)


        elif command == "settings":
            cp.cmd_settings()
        elif command == "set":
            (setting_name, sep, value) = rem.partition(" ")
            value = value.strip()
            cp.cmd_set_setting(setting_name, value)
        elif command == "dump":
            print "Result set: %s" % result_set.output()
        elif command == "reset":
            result_set = ResultSet()
        elif command == "episode_list":
            print "Looking up episode list for: '%s'" % result_set.details.title.encode('ascii', 'xmlcharrefreplace')
            cp.cmd_episode_list(result_set.details)
        elif command == "episode_details":
            try:
                which = int(rem) - 1
            except ValueError:
                print "** '%s' must be an integer." % rem
                continue
            cp.cmd_episode_details(result_set.details.episodes[which])
        else:
            print "** '%s' is not a valid command."

    return

############################################################################
############################################################################
#
# Here is where it all starts
#
if __name__ == "__main__":
    main()
#
#
############################################################################
############################################################################
