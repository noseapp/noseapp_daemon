# -*- coding: utf-8 -*-

from collections import OrderedDict
from contextlib import contextmanager

from noseapp_daemon.daemon import Daemon
from noseapp_daemon.service import DaemonService


class CheckoutError(BaseException):
    pass


class ServiceManagement(object):
    """
    Interface for daemons and services control

    Example::

      class Servant(DaemonsManagement):

        def prepare(self):
          # do something...

      servant = Servant(config=app_config)
      servant.add_daemon(daemon)
      ...

      with servant.checkout_daemon('my_daemon') as my_daemon:
        my_daemon.start()

      my_service = servant.service('my_service')
      my_service.start()

      servant.stop_all()

      servant.start_all()
      servant.stop_daemons()
    """

    def __init__(self, config=None):
        self._config = config

        self.__daemons = OrderedDict()
        self.__services = OrderedDict()

        self.prepare()

    def prepare(self):
        pass

    def add_service(self, service):
        if not isinstance(service, DaemonService):
            raise TypeError('service is not instance DaemonService')

        self.__services[service.name] = service

    def add_daemon(self, daemon):
        if not isinstance(daemon, Daemon):
            raise TypeError('daemon is not instance Daemon')

        self.__daemons[daemon.name] = daemon

    def daemon(self, name):
        return self.__daemons.get(name)

    def service(self, name):
        return self.__services.get(name)

    @contextmanager
    def checkout_service(self, name):
        try:
            service = self.__services[name]
        except KeyError as e:
            raise CheckoutError(
                'Service "{}" not found'.format(e.message),
            )

        yield service

    @contextmanager
    def checkout_daemon(self, name):
        try:
            daemon = self.__daemons[name]
        except KeyError as e:
            raise CheckoutError(
                'Daemon "{}" not found'.format(e.message),
            )

        yield daemon

    def start_services(self):
        for _, service in self.__services.items():
            service.start()

    def stop_services(self):
        for _, service in self.__services.items():
            service.stop()

    def restart_services(self):
        self.stop_services()
        self.start_services()

    def start_daemons(self):
        for _, daemon in self.__daemons.items():
            daemon.start()

    def stop_daemons(self):
        for _, daemon in self.__daemons.items():
            daemon.stop()

    def restart_daemons(self):
        self.stop_daemons()
        self.start_daemons()

    def start_all(self):
        self.start_daemons()
        self.start_services()

    def stop_all(self):
        self.stop_daemons()
        self.stop_services()

    def restart_all(self):
        self.stop_all()
        self.start_all()
