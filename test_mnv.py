#!/usr/bin/env python3

import socket
import uuid

# from mnvpostoffice.NetworkTypes import IPv4Address
# from mnvpostoffice.Routing import MessageTerminus, PostOffice
# from mnvpostoffice.Envelope import Message, Subscription

from mnvruncontrol.backend.PostOffice.NetworkTypes import IPv4Address
from mnvruncontrol.backend.PostOffice.Routing import MessageTerminus, PostOffice
from mnvruncontrol.backend.PostOffice.Envelope import Message, Subscription


def wtf():
    ident = uuid.uuid4()

    # term = MessageTerminus()
    po = PostOffice(listen_port=9998)
    # po = PostOffice()

    # po.Startup()

    po.AddSubscription(Subscription(subject='mgr_directive', action=Subscription.FORWARD, delivery_address=IPv4Address('127.0.0.1', 1090)))
    po.AddSubscription(Subscription(subject='control_request', action=Subscription.FORWARD, delivery_address=IPv4Address('127.0.0.1', 1090)))

    # po.subscriptions[0].delivery_address = IPv4Address('127.0.0.1', 9998)
    # po.subscriptions[0].delivery_address = term

    msg = Message(subject='mgr_directive', directive='status_report', client_id=ident)

    resp = po.SendAndWaitForResponse(msg, timeout=5000)


class MyTerm(MessageTerminus):
    def __init__(self):
        super().__init__(self)

        self.ident = uuid.uuid4()

        # self.po = PostOffice(listen_port=3000)
        self.po = PostOffice(listen_port=9998) # listen_port seems to be mandatory
        # self.po = PostOffice()

        # subscriptions = [ Subscription(subject="mgr_status", action=Subscription.DELIVER, delivery_address=self),
        #                   Subscription(subject="client_alert", action=Subscription.DELIVER, delivery_address=self),
        #                   Subscription(subject="frontend_internal", action=Subscription.DELIVER, delivery_address=self),
        #                   Subscription(subject="frontend_info", action=Subscription.DELIVER, delivery_address=self) ]

        # handlers = [self.handle_message1, self.handle_message2, self.handle_message3, self.handle_message4]

        # for sub, handler in zip(subscriptions, handlers):
        #     self.po.AddSubscription(sub)
        #     self.AddHandler(sub, handler)

        self.po.AddSubscription(Subscription(subject='control_request', action=Subscription.FORWARD, delivery_address=('127.0.0.1', 1090)))
        self.po.AddSubscription(Subscription(subject='mgr_directive', action=Subscription.FORWARD, delivery_address=('127.0.0.1', 1090)))

    def status(self):
        msg = Message(subject='mgr_directive', directive='status_report', client_id=self.ident)
        resp = self.po.SendAndWaitForResponse(msg, timeout=20)
        return resp

    def get_control(self):
        my_ip = socket.gethostbyname(socket.gethostname())
        msg = Message(subject='control_request', request='get', requester_id=self.ident,
                      requester_name='Bart', requester_ip=my_ip, requester_location='MINOS',
                      requester_phone='630-999-9999')
        resp = self.po.SendAndWaitForResponse(msg, timeout=20)
        return resp

    def start_run(self):
        # Call get_control first
        status = self.status()
        msg = Message(subject='mgr_directive', directive='start', client_id=self.ident,
                      configuration=status[0].status['configuration'])
        return self.po.SendAndWaitForResponse(msg, timeout=5)

    # def handle_message1(self, message):
    #     print('Got a message1!')
    #     print(message)

    # def handle_message2(self, message):
    #     print('Got a message2!')
    #     print(message)

    # def handle_message3(self, message):
    #     print('Got a message3!')
    #     print(message)

    # def handle_message4(self, message):
    #     print('Got a message4!')
    #     print(message)


def status_standalone():
    ident = uuid.uuid4()
    po = PostOffice(listen_port=9998) # listen_port seems to be mandatory
    po.AddSubscription(Subscription(subject='mgr_directive', action=Subscription.FORWARD, delivery_address=('127.0.0.1', 1090)))
    msg = Message(subject='mgr_directive', directive='status_report', client_id=ident)
    return po.SendAndWaitForResponse(msg, timeout=20)
