
============
Installation
============

::

  pip install noseapp_daemon


====
Why?
====

I testing linux daemon with noseapp lib and i wont have ability control for daemon running, prepare... something else...


====
How?
====

Create Runner::

  from noseapp.ext.daemon import Daemon

  class MyDaemon(Daemon):

    name = 'my_daemon'

    @property
    def cmd(self):
      return [
        self.daemon_bin,
        '--config',
        self.options['config_file'],
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

    def setup(self):
      self.prepare_db()
      self._my_daemon = MyDaemon(
        self._config.MY_DAEMON_BIN,
        config_file=self._config.MY_DAEMON_CONFIG_PATH,
      )

    def prepare_db(self):
      self._options['db'] ...

    def start(self):
      self._my_daemon.start()

    ...


Create Management::

  from noseapp.ext.daemon import DaemonManagement

  class MyDaemonManagement(DaemonManagement):

    def setup(self):
        self.add_daemon(
          MyDaemon(
            self._app.config.MY_DAEMON_BIN,
            config_file=self._app.config.MY_DAEMON_CONFIG_PATH,
          ),
        )

        self.add_service(
          MyDaemonService(self._app.config, db=DBClient(...)),
        )

     ...

  management = MyDaemonManagement(app)
  management.start_all()

  with management.checkout_daemon(
    'my_daemon',
    ignore_exc=(TypeError,),
    callback=lambda: None,  # if ValueError will be raise, this function can be called
  ) as my_daemon:
    my_daemon.stop()

  management.service('my_daemon_service').stop()

  # management.stop_all()
  # management.stop_daemons()
  # management.stop_services()
  # management.restart_all()
  # etc ...
