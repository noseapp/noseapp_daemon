# -*- coding: utf-8 -*-

from collections import OrderedDict
from contextlib import contextmanager

from noseapp_daemon.runner import DaemonRunner
from noseapp_daemon.service import DaemonService


class ServiceNotFound(LookupError):
    pass


class DaemonNotFound(LookupError):
    pass


class DaemonManagement(object):
    """
    Interface for daemons and services control

    Example::

      class MyDaemonManagement(DaemonManagement):

        def setup(self):
          # do something...

      management = MyDaemonManagement(app)
      management.add_daemon(daemon)
      ...

      with management.checkout_daemon(
        'my_daemon',
        except_exc=(ValueError,),
        error_handler=lambda daemon, error: None,
      ) as my_daemon:
        my_daemon.start()

      management.service('my_service').start()

      management.stop_all()

      management.start_all()
      management.stop_daemons()
      ...
    """

    def __init__(self, app=None, options=None):
        self.options = options

        self._app = app

        self.__daemons = OrderedDict()
        self.__services = OrderedDict()

        self.setup()

    @property
    def services(self):
        return self.__services

    @property
    def daemons(self):
        return self.__daemons

    def setup(self):
        pass

    def add_service(self, service):
        if not isinstance(service, DaemonService):
            raise TypeError('"service" param is not instance of "DaemonService"')

        self.__services[service.name] = service

    def add_daemon(self, daemon):
        if not isinstance(daemon, DaemonRunner):
            raise TypeError('"daemon" param is not instance of "DaemonRunner"')

        self.__daemons[daemon.name] = daemon

    def daemon(self, name):
        try:
            daemon = self.__daemons[name]
        except KeyError:
            raise DaemonNotFound(name)

        return daemon

    def service(self, name):
        try:
            service = self.__services[name]
        except KeyError:
            raise ServiceNotFound(name)

        return service

    @contextmanager
    def checkout_service(self, name, except_exc=None, error_handler=None):
        service = self.service(name)

        if isinstance(except_exc, tuple) or isinstance(except_exc, BaseException):
            try:
                yield service
            except except_exc as e:
                if callable(error_handler):
                    error_handler(service, e)
        else:
            yield service

    @contextmanager
    def checkout_daemon(self, name, except_exc=None, error_handler=None):
        daemon = self.daemon(name)

        if isinstance(except_exc, tuple) or isinstance(except_exc, BaseException):
            try:
                yield daemon
            except except_exc as e:
                if callable(error_handler):
                    error_handler(daemon, e)
        else:
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
