#!/usr/bin/env python3

import argparse
import toml

from .db import DB
from .subsystems.crs import CrsController
from .subsystems.lrs import LrsController
# from .subsystems.minerva import MinervaController

SUBSYSTEMS = {
    'crs': CrsController,
    'lrs': LrsController,
    # 'minerva': MinervaController
}

class MORCS:
    def __init__(self, config: dict):
        self.config = config
        self.db = DB(config)

        self.subsystems = [SUBSYSTEMS[k](config, self.db)
                           for k in config['global']['subsystems']]

    def start_run(self):
        for s in self.subsystems:
            s.start_run()
        self.db.start_run()

    def stop_run(self):
        for s in self.subsystems:
            s.stop_run()
        self.db.stop_run()

def main():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('--cfg', help='Config file', default='morcs.toml')

    subp = ap.add_subparsers(title='subcommands', dest='subcommand')
    subp.add_parser('start-run')
    subp.add_parser('stop-run')

    args = ap.parse_args()

    config = toml.load(open(args.cfg, 'r'))
    app = MORCS(config)

    if args.subcommand == 'start-run':
        app.start_run()
    elif args.subcommand == 'stop-run':
        app.stop_run()
    else:
        ap.print_usage()
