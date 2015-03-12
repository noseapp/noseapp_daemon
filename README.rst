
====
Why?
====

I testing daemon with noseapp lib and i wont have ability control for running, prepare... something else...


====
How?
====

Create Daemon::

  from noseapp.ext.daemon import Daemon

  class MyDaemon(Daemon):

    name = 'my_daemon'

    @property
    def cmd(self):
      return [
        self.daemon_bin,
        '--config',
        self.config_file,
      ]

    def before_start(self):
      # do something...
      # see another callbacks


  my_daemon = MyDaemon('path/to/my_daemon/bin', config_file='path/to/config/file')
  my_daemon.start()


Create Service::

  from noseapp.ext.daemon import DaemonService

  class MyDaemonService(DaemonService):

    name = 'my_daemon_service'

    def __init__(self, config, db):
      self._db = db
      self._my_daemon = MyDaemon(
        config.MY_DAEMON_BIN,
        config_file=config.MY_DAEMON_CONFIG_PATH,
      )
      self.prepare_db()

    def prepare_db(self):
      self._db ...

    def start(self):
      self._my_daemon.start()

    ...


Management::

  from noseapp.ext.daemon import ServiceManagement

  class MyServiceManagement(ServiceManagement):

    def prepare(self):
        self.add_daemon(
          MyDaemon(
            config.MY_DAEMON_BIN,
            config_file=config.MY_DAEMON_CONFIG_PATH,
          ),
        )

        self.add_service(
          MyDaemonService(self._config, DBClient(...)),
        )

  management = MyServiceManagement(config=app_config)
  management.start_all()

  with management.checkout_daemon('my_daemon') as my_daemon:
    my_daemon.stop()

  my_daemon_service = management.service('my_daemon_service')
  my_daemon_service.stop()

  # management.stop_all()
  # management.stop_daemons()
  # management.stop_services()
  # management.restart_all()
  # etc ...
