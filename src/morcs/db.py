#!/usr/bin/env python3

import datetime

from sqlalchemy import create_engine, func, select, insert, update
from sqlalchemy import MetaData, Table, Column, Integer, DateTime, String
from .util import connect_krbrs

metadata = MetaData()

RunData = Table('run_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('source', String),
    Column('start_time', DateTime),
    Column('end_time', DateTime))


class DB:
    def __init__(self, config: dict):
        self.config = config
        self.engine = create_engine(f'sqlite:///{config["global"]["db"]}')
        metadata.create_all(self.engine)

    def latest_run(self):
        with self.engine.connect() as conn:
            q = select(func.max(RunData.c.id))
            latest = conn.execute(q).one()[0]
        return 0 if (latest is None) else latest

    def next_run(self):
        run = self.latest_run() + 1
        if min_run := self.config['global'].get('min_run'):
            if run < min_run:
                return min_run
        return run

    def start_run(self):
        with self.engine.begin() as txn:
            txn.execute(
                insert(RunData),
                {'id': self.next_run(),
                 'source': self.config['global']['source'],
                 'start_time': datetime.datetime.now()})

    def stop_run(self):
        with self.engine.begin() as txn:
            sel = RunData.c.id == select(func.max(RunData.c.id)).scalar_subquery()
            txn.execute(update(RunData).where(sel),
                        {'end_time': datetime.datetime.now()})
        BC_dir = self.config['global']["blobcraft_dir"]

        with connect_krbrs(self.config['lrs']['ssh_host']) as conn:
            rmt_path = self.config['lrs']['db_path']              #remote path
            lcl_path = BC_dir + '/config/lrsdetconfig.db'         #local path
            conn.get(rmt_path, local = lcl_path)

            
