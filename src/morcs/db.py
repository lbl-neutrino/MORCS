#!/usr/bin/env python3

import datetime

from sqlalchemy import create_engine, func, select, insert, update
from sqlalchemy import MetaData, Table, Column, Integer, DateTime


metadata = MetaData()

RunData = Table('run_data', metadata,
    Column('id', Integer, primary_key=True),
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
        return run

    def start_run(self):
        with self.engine.begin() as txn:
            txn.execute(
                insert(RunData),
                {'id': self.next_run(),
                 'start_time': datetime.datetime.now()})

    def stop_run(self):
        with self.engine.begin() as txn:
            sel = RunData.c.id == select(func.max(RunData.c.id)).scalar_subquery()
            txn.execute(update(RunData).where(sel),
                        {'end_time': datetime.datetime.now()})
