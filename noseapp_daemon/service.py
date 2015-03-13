# -*- coding: utf-8 -*-


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

    def __init__(self, config=None, **options):
        self._config = config
        self._options = options

        self.setup()

    def setup(self):
        pass

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
