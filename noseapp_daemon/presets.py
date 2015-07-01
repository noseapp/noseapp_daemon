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

    DAEMON_BIN = utils.which('nginx', default='/usr/sbin/nginx')

    @property
    def name(self):
        return 'nginx'


class TarantoolDaemon(DaemonRunner):
    """
    Preset for tarantool box

    Usage:
        from noseapp.daemon.presets import NGINXDaemon

        tnt = TarantoolDaemon()
        tnt.add_option('-c', '/path/to/config_file.cfg')
        tnt.start()
    """

    DAEMON_BIN = utils.which('tarantool_box')

    @property
    def name(self):
        return 'tarantool'

    @staticmethod
    def remove_snapshots():
        logger.debug('Remove tarantool snapshots')

        for filename in glob.glob('*.snap'):
            os.unlink(filename)

        for filename in glob.glob('*.xlog'):
            os.unlink(filename)

    def init_storage(self, **kwargs):
        logger.debug('Init tarantool storage')

        kwargs.update(shell=True)
        cmd_options = ' --init-storage'
        cmd = self.get_cmd() + cmd_options
        exit_code = subprocess.call(cmd, **kwargs)

        if exit_code > 0:
            raise DaemonError('Init storage error')
