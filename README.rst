
============
Installation
============

::

  pip install noseapp_daemon


=============
Create Runner
=============

::

  from noseapp.ext.daemon import DaemonRunner

  class MyPythonDaemon(DaemonRunner):

      CMD_PREFIX = 'python'
      DAEMON_BIN = '/path/to/daemon/daemon.py'


  my_daemon = MyPythonDaemon('my_daemon')
  my_daemon.add_cmd_option('-c', '/path/to/config')
  my_daemon.start()


====================
Create daemon plugin
====================

::

  from noseapp.ext.daemon import DaemonPlugin


  class MyPythonDaemonPlugin(DaemonPlugin):

      def init(self, daemon):
          # do something

      def before_start(self, daemon):
          # do something

      def after_start(self, daemon):
          # do something

      def before_stop(self, daemon):
          # do something

      def after_stop(self, daemon):
          # do something


  my_daemon = MyPythonDaemon('my_daemon', plugin=MyPythonDaemonPlugin())


==============
Create Service
==============

::

  from noseapp.ext.daemon import DaemonService

  class MyDaemonService(DaemonService):

    name = 'my_service'

    def setup(self):
        self.daemon = MyPythonDaemon('my_daemon')

    def start(self):
        self.daemon.start()

    def stop(self):
        self.daemon.stop()

    ...


  service = MyDaemonService()
  service.start()
  service.restart()


=================
Create Management
=================

::

  from noseapp.ext.daemon import DaemonManagement

  management = DaemonManagement(app)
  management.add_daemon(
      MyPythonDaemon('my_daemon', plugin=MyPythonDaemonPlugin()),
  )
  daemon = management.daemon('my_daemon')

  def error_handler(daemon, e):
      # do something

  with management.checkout_daemon('my_daemon', except_exc=Exception, error_handler=error_handler) as daemon:
      daemon.restart()

  management.add_service(MyDaemonService())
  service = management.service('my_service')
  ...

  # management.stop_all()
  # management.stop_daemons()
  # management.stop_services()
  # management.restart_all()
  # etc ...


=======
Presets
=======

::

  noseapp.ext.daemon.presets import NGINXDaemon
  noseapp.ext.daemon.presets import UWSGIDaemon
  ...


  nginx = NGINXDaemon()
  uwsgi = UWSGIDaemon()

  nginx.add_cmd_option('-c', '/path/to/config')
  uwsgi.add_dmd_option('--ini', '/path/to/config')

  nginx.start()
  uwsgi.start()
  ...
