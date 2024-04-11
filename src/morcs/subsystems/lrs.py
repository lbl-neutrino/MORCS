#!/usr/bin/env python3

import requests

from ..controller import DaqController

class LrsController(DaqController):
    def get_url(self, function):
        host = self.config['lrs']['host']
        return f'http://{host}/api/{function}/'

    def start_run(self):
        params = {
            'run': self.db.next_run(),
        }
        if stream := self.config['global'].get('data_stream'):
            params['data_stream'] = stream
        url = self.get_url('start_data_run')
        requests.post(url, json=params)

    def stop_run(self):
        url = self.get_url('stop_data_run')
        requests.get(url)
