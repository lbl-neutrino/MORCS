#!/usr/bin/env python3

import os
import uuid

from .base import DaqController


class CrsController(DaqController):
    def start_run(self):
        self.pidfile = f'/tmp/crs.{uuid.uuid4()}.pid'

        # TODO: Escape quotes, etc.
        inner_cmd = self.config['crs']['start_cmd']

        host = self.config['crs']['host']
        cmd = f'ssh {host}'
        cmd += f" 'nohup {inner_cmd} >/dev/null 2>&1 & echo $! > {self.pidfile}"
        os.system(cmd)

    def stop_run(self):
        inner_cmd = f'kill $(cat {self.pidfile}) && rm {self.pidfile}'
        host = self.config['crs']['host']
        cmd = f"ssh {host} '{inner_cmd}'"
        os.system(cmd)
