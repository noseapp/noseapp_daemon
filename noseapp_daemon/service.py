# -*- coding: utf-8 -*-

import abc


class DaemonService(object):
    """
    Abstract layer for daemon run logic realization

    Example::

      class MyDaemonService(DaemonService):

        def setup(self):
          self._daemon = MyDaemon(self._config...)
          # do something...

        # your interface for daemon management here

        def start():
          self._daemon.start()
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None, options=None):
        self.options = options

        self._config = config

        self.setup()

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def setup(self):
        pass
