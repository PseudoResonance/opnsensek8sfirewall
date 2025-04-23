#!/usr/bin/env python3

import argparse
from opnsensek8sfirewall.main import main

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dryrun",
    action="store_true",
    help="Output computed options without updating OPNSense",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Output extra info while running",
)
parser.add_argument(
    "-c",
    "--config",
    default="./config.json",
    help="Specify the config file path",
)

if __name__ == "__main__":
    args = parser.parse_args()
    main(dryRun=args.dryrun, verbose=args.verbose, configPath=args.config)
