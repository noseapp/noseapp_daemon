# -*- coding: utf-8 -*-

"""
Fake daemon for testing DaemonRunner class
"""

import os
import time

from noseapp_daemon.runner import DaemonRunner
from noseapp_daemon.service import DaemonService


PYTHON_BIN = 'python'
SELF_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'daemon.py',
    ),
)


def create_fake_daemon(name='test', **kwargs):
    return DaemonRunner(
        name,
        cmd_prefix=PYTHON_BIN,
        daemon_bin=SELF_PATH,
        **kwargs
    )


class TestService(DaemonService):

    name = 'test_service'

    def setup(self):
        self.daemon = create_fake_daemon()

    def start(self):
        self.daemon.start()

    def stop(self):
        self.daemon.stop()


if __name__ == '__main__':
    while True:
        time.sleep(1)
