# -*- coding: utf-8 -*-

import abc


class DaemonService(object):
    """
    Abstract layer for daemon run logic implementation
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None, options=None):
        self.__options = options
        self.__config = config

        self.daemon = None

        self.setup()

    @property
    def config(self):
        return self.__config

    @property
    def options(self):
        return self.__options

    def restart(self):
        self.stop()
        self.start()

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass
