#!/usr/bin/env python3

import requests

from ..controller import DaqController

class LrsController(DaqController):
    def get_url(self, function):
        host = self.config['lrs']['daq_host']
        port = self.config['lrs']['daq_port']
        return f'http://{host}:{port}/api/{function}/'

    def start_run(self):
        params = {
            'run': self.db.next_run(),
            'run_starting_instance': 'morcs',
        }
        if stream := self.config['global'].get('data_stream'):
            params['data_stream'] = stream
        url = self.get_url('start_data_run')
        requests.post(url, json=params)

    def stop_run(self):
        url = self.get_url('stop_data_run')
        requests.get(url)
