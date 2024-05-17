#!/usr/bin/env python3

from time import strftime

from fabric import Connection, Result

from ..controller import DaqController
from ..db import DB


class CrsController(DaqController):
    def __init__(self, config: dict, db: DB):
        super().__init__(config, db)
        connect_kwargs = {'gss_auth': True, 'gss_kex': True}
        self.conn = Connection(config['crs']['host'],
                               connect_kwargs=connect_kwargs)

    def datafile(self, run: int):
        packet = self.config['crs'].get('packet')
        prefix = 'packet' if packet else 'binary'
        tstamp = strftime("%Y_%m_%d_%H_%M_%S_%Z")
        return f'{prefix}-{run:07}-{tstamp}.hdf5'

    def run_in_screen(self, cmds: list[str]):
        screen = self.config['crs']['screen_session']
        for cmd in cmds:
            qcmd = cmd.replace('"', '\\"')
            fullcmd = f'screen -S {screen} -X stuff "{qcmd}\r"'
            self.conn.run(fullcmd, warn=True)

    def ctrlc_in_screen(self):
        screen = self.config['crs']['screen_session']
        fullcmd = f'screen -S {screen} -X stuff "^C"'
        self.conn.run(fullcmd, warn=True)

    def start_run(self):
        opts = []
        if self.config['crs'].get('packet'):
            opts.append('--packet')
        if runtime := self.config['crs'].get('runtime_sec'):
            opts.append(f'--runtime {runtime}')
        # We need file_count = 1 when specifying the filename
        file_count = self.config['crs'].get('file_count', -1)
        opts.append(f'--file_count {file_count}')
        if cfg := self.config['crs'].get('pacman_cfg'):
            opts.append(f'--pacman_config "{cfg}"')
        opts.append('--record_metadata')

        run = self.db.next_run()

        opts.append(f'--run {run}')
        if stream := self.config['global'].get('data_stream'):
            opts.append(f'--data_stream {stream}')

        filename = self.datafile(run)
        # opts.append(f'--filename "{filename}"')
        opts.append(f'--file_tag {run:07}')

        inner_cmd = f'python record_data.py {" ".join(opts)}'

        log_dir = self.config['crs']['log_dir']
        log_path = f'{log_dir}/{filename}.log'

        cmds = [
            f'mkdir -p "{log_dir}"',
            # f'{inner_cmd} >> "{log_path}" 2>&1'
            f'{inner_cmd}'
        ]

        print('\n'.join(cmds))

        self.run_in_screen(cmds)

    def stop_run(self):
        self.ctrlc_in_screen()
