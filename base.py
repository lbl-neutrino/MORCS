#!/usr/bin/env python3

from abc import ABC, abstractmethod

class DaqController(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def start_run(self):
        pass

    @abstractmethod
    def stop_run(self):
        pass
