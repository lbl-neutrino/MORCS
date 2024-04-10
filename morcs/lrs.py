#!/usr/bin/env python3

from enum import Enum
import socket
import uuid

from .base import DaqController


class LrsMsgType(Enum):
    CONFIG_V4 = 0xAE2E6D03
    CMD_V4 = 0xAE2E6D04


def encode(msgtype: LrsMsgType, cmd: str, *args: str) -> bytes:
    payload = ' '.join([cmd, *args]).encode() + b'\r\n'
    magic = msgtype.value.to_bytes(4, 'little')
    length = len(payload).to_bytes(4, 'little')
    return magic + length + payload


class LrsController(DaqController):
    def __init__(self, config: dict):
        super().__init__(config)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((config['lrs'].get('remote_addr', 'localhost'),
                           config['lrs'].get('remote_port', 33334)))

    def send(self, msgtype: LrsMsgType, cmd: str, *args: str):
        msg = encode(msgtype, cmd, *args)
        self.sock.sendall(msg)

    def start_run(self):
        self.uuid = str(uuid.uuid4())

        self.send(LrsMsgType.CMD_V4,
                  'start',
                  self.config['lrs'].get('global_index', '0'),
                  self.config['lrs'].get('run', '0'),
                  self.uuid)

    def stop_run(self):
        self.send(LrsMsgType.CMD_V4,
                  'stop',
                  self.config['lrs'].get('global_index', '0'),
                  self.config['lrs'].get('run', '0'),
                  self.uuid)
