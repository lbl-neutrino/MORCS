#!/usr/bin/env python3

from abc import ABC, abstractmethod

from .db import DB

class DaqController(ABC):
    def __init__(self, config: dict, db: DB):
        self.config = config
        self.db = db

    @abstractmethod
    def start_run(self):
        pass

    @abstractmethod
    def stop_run(self):
        pass
