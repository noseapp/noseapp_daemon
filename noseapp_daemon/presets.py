# -*- coding: utf-8 -*-

import os
import glob
import logging
import subprocess

from noseapp_daemon import utils
from noseapp_daemon.runner import DaemonError
from noseapp_daemon.runner import DaemonRunner


logger = logging.getLogger(__name__)


class NGINXDaemon(DaemonRunner):
    """
    Preset for nginx daemon

    Usage:
        from noseapp.daemon.presets import NGINXDaemon

        nginx = NGINXDaemon()
        nginx.add_option('-c', '/path/to/config_file.cfg')
        nginx.start()
    """

    DEFAULT_NAME = 'nginx'
    DAEMON_BIN = utils.which('nginx', default='/usr/sbin/nginx')

    @property
    def name(self):
        if self._name:
            return self._name
        return self.DEFAULT_NAME


class TarantoolDaemon(DaemonRunner):
    """
    Preset for tarantool box

    Usage:
        from noseapp.daemon.presets import NGINXDaemon

        tnt = TarantoolDaemon()
        tnt.add_option('-c', '/path/to/config_file.cfg')
        tnt.start()
    """

    DEFAULT_NAME = 'tarantool'
    DAEMON_BIN = utils.which('tarantool_box')

    @property
    def name(self):
        if self._name:
            return self._name
        return self.DEFAULT_NAME

    @staticmethod
    def remove_snapshots():
        logger.debug('Remove tarantool snapshots')

        for filename in glob.iglob('*.snap'):
            os.unlink(filename)

        for filename in glob.iglob('*.xlog'):
            os.unlink(filename)

    def init_storage(self, **kwargs):
        logger.debug('Init tarantool storage')

        kwargs.update(shell=True)
        cmd_options = ' --init-storage'
        cmd = self.get_cmd() + cmd_options
        exit_code = subprocess.call(cmd, **kwargs)

        if exit_code > 0:
            raise DaemonError('Init storage error')


class UWSGIDaemon(DaemonRunner):

    DEFAULT_NAME = 'uwsgi'
    DAEMON_BIN = utils.which('uwsgi', default='/usr/local/bin/uwsgi')

    @property
    def name(self):
        if self._name:
            return self._name
        return self.DEFAULT_NAME
