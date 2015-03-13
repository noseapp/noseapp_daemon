# -*- coding: utf-8 -*-

from collections import OrderedDict
from contextlib import contextmanager

from noseapp_daemon.runner import DaemonRunner
from noseapp_daemon.service import DaemonService


class ServiceNotFound(BaseException):
    pass


class DaemonNotFound(BaseException):
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
        ignore_exc=(ValueError,),
        callback=lambda: None,  # if ValueError will be raised, this function can be called
      ) as my_daemon:
        my_daemon.start()

      management.service('my_service').start()

      management.stop_all()

      management.start_all()
      management.stop_daemons()
      ...
    """

    def __init__(self, app=None, **options):
        self._app = app
        self._options = options

        self.__daemons = OrderedDict()
        self.__services = OrderedDict()

        self.setup()

    def setup(self):
        pass

    def add_service(self, service):
        if not isinstance(service, DaemonService):
            raise TypeError('"service" param is not instance "DaemonService"')

        self.__services[service.name] = service

    def add_daemon(self, daemon):
        if not isinstance(daemon, DaemonRunner):
            raise TypeError('"daemon" param is not instance "DaemonRunner"')

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
    def checkout_service(self, name, ignore_exc=None, callback=None):
        if isinstance(ignore_exc, tuple):
            try:
                yield self.service(name)
            except ignore_exc:
                if callable(callback):
                    callback()
        else:
            yield self.service(name)

    @contextmanager
    def checkout_daemon(self, name, ignore_exc=None, callback=None):
        if isinstance(ignore_exc, tuple):
            try:
                yield self.daemon(name)
            except ignore_exc:
                if callable(callback):
                    callback()
        else:
            yield self.daemon(name)

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
