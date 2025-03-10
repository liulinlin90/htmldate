"""
Implementing a basic command-line interface.
"""

## This file is available from https://github.com/adbar/htmldate
## under GNU GPL v3 license

import argparse
import sys

from platform import python_version

from . import __version__
from .core import find_date
from .utils import fetch_url
from .settings import MIN_FILE_SIZE, MAX_FILE_SIZE


def examine(htmlstring, extensive_bool=True, original_date=False,
            verbose_flag=False, mindate=None, maxdate=None):
    """ Generic safeguards and triggers """
    # safety check
    if htmlstring is None:
        sys.stderr.write('# ERROR: empty document\n')
    elif len(htmlstring) > MAX_FILE_SIZE:
        sys.stderr.write('# ERROR: file too large\n')
    elif len(htmlstring) < MIN_FILE_SIZE:
        sys.stderr.write('# ERROR: file too small\n')
    else:
        return find_date(htmlstring, extensive_search=extensive_bool,
                           original_date=original_date, verbose=verbose_flag,
                           min_date=mindate, max_date=maxdate)
    return None


def parse_args(args):
    """Define parser for command-line arguments"""
    argsparser = argparse.ArgumentParser()
    argsparser.add_argument("-f", "--fast",
                            help="fast mode: disable extensive search",
                            action="store_false")
    argsparser.add_argument("-i", "--inputfile",
                            help="""name of input file for batch processing
                            (similar to wget -i)""",
                            type=str)
    argsparser.add_argument("--original",
                            help="original date prioritized",
                            action="store_true")
    argsparser.add_argument("-min", "--mindate",
                            help="earliest acceptable date (YYYY-MM-DD)",
                            type=str)
    argsparser.add_argument("-max", "--maxdate",
                            help="latest acceptable date (YYYY-MM-DD)",
                            type=str)
    argsparser.add_argument("-u", "--URL",
                            help="custom URL download",
                            type=str)
    argsparser.add_argument("-v", "--verbose",
                            help="increase output verbosity",
                            action="store_true")
    argsparser.add_argument("--version",
                            help="show version information and exit",
                            action="version",
                            version="Htmldate {} - Python {}".format(
                            __version__, python_version()
                            ),)
    return argsparser.parse_args()


def process_args(args):
    """Process the arguments passed on the command-line."""
    if not args.inputfile:
        # URL as input
        if args.URL:
            htmlstring = fetch_url(args.URL)
            if htmlstring is None:
                sys.exit('# ERROR no valid result for url: ' + args.URL + '\n')
        # unicode check
        else:
            try:
                htmlstring = sys.stdin.read()
            except UnicodeDecodeError as err:
                sys.exit('# ERROR system/buffer encoding: ' + str(err) + '\n')
        result = examine(htmlstring, extensive_bool=args.fast,
                         original_date=args.original,
                         verbose_flag=args.verbose,
                         maxdate=args.maxdate)
        if result is not None:
            sys.stdout.write(result + '\n')

    # process input file line by line
    else:
        with open(args.inputfile, mode='r', encoding='utf-8') as inputfile:
            for line in inputfile:
                htmltext = fetch_url(line.strip())
                result = examine(htmltext, extensive_bool=args.fast,
                                 original_date=args.original,
                                 verbose_flag=args.verbose,
                                 mindate=args.mindate, maxdate=args.maxdate)
                if result is None:
                    result = 'None'
                sys.stdout.write(line.strip() + '\t' + result + '\n')


def main():
    """ Run as a command-line utility. """
    # arguments
    args = parse_args(sys.argv[1:])
    # process input on STDIN
    process_args(args)


if __name__ == '__main__':
    main()
