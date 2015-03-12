# -*- coding: utf-8 -*-


class DaemonService(object):
    """
    Abstract layer for realization logic of daemon

    Example::

      class MyDaemonService(DaemonService):

        def __init__(self...):
          self._daemon = MyDaemon(...)
          # do something...

        # your interface for daemon management here

        def start():
          self._daemon.start()
    """

    @property
    def name(self):
        raise NotImplementedError(
            'Property "name" should be implemented in subclasses.',
        )

    def start(self):
        raise NotImplementedError(
            'Method "start" should be implemented in subclasses.',
        )

    def stop(self):
        raise NotImplementedError(
            'Method "stop" should be implemented in subclasses.',
        )

    def restart(self):
        self.stop()
        self.start()
