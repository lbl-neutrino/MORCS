#!/usr/bin/env python3

import socket
import time
import uuid

from ..controller import DaqController

from mnvruncontrol.backend.PostOffice.Routing import PostOffice
from mnvruncontrol.backend.PostOffice.Envelope import Message, Subscription


MAGIC_SLEEP_SEC = 10


class MinervaController(DaqController):
    def __init__(self, config: dict, db):
        super().__init__(config, db)

        self.ident = uuid.uuid4()
        self.ip = socket.gethostbyname(socket.gethostname())

        port = config['minerva'].get('listen_port', 9998)
        self.postoffice = PostOffice(listen_port=port)

        server = (config['minerva'].get('remote_addr', 'localhost'),
                  config['minerva'].get('remote_port', 1090))

        for subject in ['mgr_directive', 'control_request']:
            sub = Subscription(subject=subject,
                               action=Subscription.FORWARD,
                               delivery_address=server)
            self.postoffice.AddSubscription(sub)

    def send(self, message: Message):
        return self.postoffice.SendAndWaitForResponse(message)

    def status(self):
        msg = Message(subject='mgr_directive',
                      directive='status_report',
                      client_id=self.ident)
        return self.send(msg)

    def update_control(self, control: bool):
        request = 'get' if control else 'release'
        msg = Message(subject='control_request',
                      request=request,
                      requester_id=self.ident,
                      requester_name='Bart',
                      requester_ip=self.ip,
                      requester_location='MINOS',
                      requester_phone='630-999-9999')
        return self.send(msg)

    def get_control(self):
        return self.update_control(True)

    def release_control(self):
        return self.update_control(False)

    def start_run(self):
        self.get_control()
        time.sleep(MAGIC_SLEEP_SEC)
        status = self.status()
        # config is a DAQConfiguration
        config = status[0].status['configuration']
        config.run = self.db.next_run()
        config.subrun = 1
        msg = Message(subject='mgr_directive',
                      directive='start',
                      client_id=self.ident,
                      configuration=config)
        response = self.send(msg)
        self.release_control()
        return response

    def stop_run(self):
        self.get_control()
        time.sleep(MAGIC_SLEEP_SEC)
        msg = Message(subject='mgr_directive',
                      directive='stop',
                      client_id=self.ident)
        response = self.send(msg)
        self.release_control()
        return response
