#!/usr/bin/env python3

from fabric import Connection, Result

from ..controller import DaqController
from ..db import DB


class CrsController(DaqController):
    def __init__(self, config: dict, db: DB):
        super().__init__(config, db)
        self.conn = Connection(config['crs']['host'])

    def preamble(self):
        venv_dir = self.config['crs']['remote_venv_dir']
        daq_dir = self.config['crs']['remote_daq_dir']

        cmds = [
            # Ensure that failures mid-pipe get reported
            f'set -o pipefail'
            f'source {venv_dir}/bin/activate',
            f'cd {daq_dir}'
        ]

        return cmds

    def pidfile(self):
        daq_dir = self.config['crs']['remote_daq_dir']
        return f'{daq_dir}/.daq.pid'

    def datafile(self, run: int):
        packet = self.config['crs'].get('packet')
        prefix = 'packet' if packet else 'binary'
        return f'{prefix}-{run:07}.hdf5'

    def start_run(self):
        opts = []
        if self.config['crs'].get('packet'):
            opts.append('--packet')
        if runtime := self.config['global'].get('runtime_sec'):
            opts.append(f'--runtime {runtime}')
        # We need file_count = 1 when specifying the filename
        opts.append('--file_count 1')
        if cfg := self.config['crs'].get('pacman_cfg'):
            opts.append(f'--pacman_config "{cfg}"')

        output_dir = self.config['crs']['output_dir']
        run = self.db.next_run()
        filename = self.datafile(run)
        opts.append(f'--filename "{output_dir}/{filename}"')

        inner_cmd = f'./record_data.py {" ".join(opts)}'

        log_dir = self.config['crs']['log_dir']
        log_path = f'{log_dir}/{filename}.log'

        cmds = [
            *self.preamble(),
            f'mkdir -p "{output_dir}" "{log_dir}"'
            f'(nohup {inner_cmd} > "{log_path}" 2>&1 & echo $! > "{self.pidfile()}")'
        ]

        r: Result = self.conn.run('&&'.join(cmds))
        assert r.return_code == 0, 'Error starting CRS DAQ'

    def stop_run(self):
        run = self.state['next_run'] - 1

        opts = []
        opts.append(f'--run {run}')
        if stream := self.config['global'].get('data_stream'):
            opts.append(f'--data-stream {stream}')

        output_dir = self.config['crs']['output_dir']
        filename = self.datafile(run)
        opts.append(f'{output_dir}/{filename}')

        cmds = [
            *self.preamble(),
            f'kill -INT $(cat {self.pidfile()})',
            f'rm {self.pidfile()}'
            f'./dump_metadata.py {" ".join(opts)}'
        ]

        r: Result = self.conn.run('&&'.join(cmds))
        assert r.return_code == 0, 'Error stopping CRS DAQ'
