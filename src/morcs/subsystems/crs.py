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

    # NOT USED:
    def preamble(self):
        venv_dir = self.config['crs']['remote_venv_dir']
        daq_dir = self.config['crs']['remote_daq_dir']

        cmds = [
            # Ensure that failures mid-pipe get reported
            # f'set -o pipefail',
            f'source {venv_dir}/bin/activate',
            f'cd {daq_dir}'
        ]

        return cmds

    # NOT USED:
    def pidfile(self):
        daq_dir = self.config['crs']['remote_daq_dir']
        return f'{daq_dir}/.daq.pid'

    def datafile(self, run: int):
        packet = self.config['crs'].get('packet')
        prefix = 'packet' if packet else 'binary'
        tstamp = strftime("%Y_%m_%d_%H_%M_%S_%Z")
        return f'{prefix}-{run:07}-{tstamp}.hdf5'

    def run_in_screen(self, cmds: list[str]):
        screen = self.config['screen_session']
        for cmd in cmds:
            qcmd = cmd.replace('"', '\\"')
            fullcmd = f'screen -S {screen} -X stuff "{qcmd}\r"'
            self.conn.run(fullcmd, warn=True)

    def ctrlc_in_screen(self):
        screen = self.config['screen_session']
        fullcmd = f'screen -S {screen} -X stuff "^C"'
        self.conn.run(fullcmd, warn=True)

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

        inner_cmd = f'python record_data.py {" ".join(opts)}'

        log_dir = self.config['crs']['log_dir']
        log_path = f'{log_dir}/{filename}.log'

        cmds = [
            f'mkdir -p "{output_dir}" "{log_dir}"',
            f'{inner_cmd} >> "{log_path}" 2>&1'
        ]

        print('\n'.join(cmds))

        self.run_in_screen(cmds)

    def stop_run(self):
        run = self.db.latest_run()

        opts = []
        opts.append(f'--run {run}')
        if stream := self.config['global'].get('data_stream'):
            opts.append(f'--data-stream {stream}')

        output_dir = self.config['crs']['output_dir']
        filename = self.datafile(run)
        opts.append(f'{output_dir}/{filename}')

        cfgdir = '/tmp/MORCS_CRS_TMPCONFIG'

        cmds = [
            f'rm -rf {cfgdir}',
            f'python monitor.py --monitor_dir {cfgdir}',
            f'python config_util/embed_config.py {filename} {cfgdir}',
            f'rm -rf {cfgdir}',
            f'python dump_metadata.py {" ".join(opts)}'
        ]

        print('\n'.join(cmds))

        self.ctrlc_in_screen()
        self.run_in_screen(cmds)
