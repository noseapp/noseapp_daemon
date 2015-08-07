# -*- coding: utf-8 -*-

import os
import logging
from collections import OrderedDict

import psutil

from noseapp_daemon import utils


logger = logging.getLogger(__name__)


def compile_cmd(
        cmd_prefix=None,
        daemon_bin=None,
        cmd_options=None,
        client_cmd=None):
    """
    Create cmd string for running
    """
    if client_cmd:
        cmd = client_cmd
    else:
        cmd = (cmd_prefix, daemon_bin, cmd_options.to_string())

    if isinstance(cmd, (list, tuple)):
        cmd = ' '.join(str(c) for c in cmd if c).strip()

    return cmd


class DaemonError(BaseException):
    pass


class CmdArgs(object):
    """
    Command line options for running daemon
    """

    def __init__(self):
        self._options = OrderedDict()

    def add_option(self, opt, value=None):
        self._options[opt] = value

    def get_option(self, opt, default=None):
        return self._options.get(opt, default)

    def to_string(self):
        string = ''

        for opt, value in self._options.items():
            if value is None or type(value) is bool:
                string += '{} '.format(opt)
            else:
                string += '{}={} '.format(opt, value)

        return string.strip()

    def __repr__(self):
        return repr(self._options)


class DaemonPlugin(object):
    """
    Class implemented callback
    interface for setup end run daemon
    """

    def init(self, daemon):
        """
        Will be called at DaemonRunner.__init__
        """
        pass

    def before_start(self, daemon):
        """
        Will be called before start daemon
        """
        pass

    def after_start(self, daemon):
        """
        Will be called after start daemon
        """
        pass

    def before_stop(self, daemon):
        """
        Will be called before stop daemon
        """
        pass

    def after_stop(self, daemon):
        """
        Will be called after stop daemon
        """
        pass


class DaemonRunner(object):
    """
    Base class for daemon run
    """

    CMD_PREFIX = None
    DAEMON_BIN = None

    plugin_class = DaemonPlugin

    def __init__(self,
                 name=None,
                 daemon_bin=None,
                 stdout=None,
                 stderr=None,
                 pid_file=None,
                 cmd_prefix=None,
                 plugin=None,
                 options=None):
        """
        :param daemon_bin: path to executable file
        :type daemon_bin: str
        :param pid_file: path to pid file
        :type pid_file: str
        :param cmd_prefix: pre start command line prefix
        :type cmd_prefix: basestring, tuple
        :param stdout: path to stdout log file.
        :type stdout: str
        :param stderr: path to stderr log file.
        :type stderr: str
        :param options: will be use as options property
        """
        self._name = name

        self.options = options
        self.cmd_args = CmdArgs()
        self.pid_file = utils.PidFileObject(pid_file)
        self.cmd_prefix = cmd_prefix or self.CMD_PREFIX
        self.daemon_bin = daemon_bin or self.DAEMON_BIN

        self.process = None

        self.stdout = stdout
        self.stderr = stderr

        self.plugin = plugin if plugin else self.plugin_class()

        if hasattr(self.plugin, 'init'):
            self.plugin.init(self)

        if not isinstance(self.daemon_bin, basestring) or not os.path.exists(self.daemon_bin):
            raise DaemonError(
                '"{}" bin file is not found'.format(self.name),
            )

    @property
    def name(self):
        """
        Name of daemon.
        """
        if not self._name:
            raise DaemonError('Daemon name is required param')

        return self._name

    @property
    def cmd(self):
        """
        Define your own command line.

        :return: list, tuple, str
        """
        return None

    @property
    def process_options(self):
        """
        Arguments for Popen __init__ method.
        """
        return {}

    @property
    def started(self):
        return bool(self.process) or self.pid_file.exist

    @property
    def stopped(self):
        return not self.started

    @property
    def is_dead(self):
        """
        To return True if process is dead else False.
        """
        try:
            return self.process.status() in (
                psutil.STATUS_DEAD,
                psutil.STATUS_ZOMBIE,
            )
        except (psutil.NoSuchProcess, AttributeError):
            return True

    def before_start(self):
        """
        Pre start callback.
        """
        if hasattr(self.plugin, 'before_start'):
            self.plugin.before_start(self)

    def after_start(self):
        """
        Post start callback.
        """
        if hasattr(self.plugin, 'after_start'):
            self.plugin.after_start(self)

    def before_stop(self):
        """
        Pre stop callback.
        """
        if hasattr(self.plugin, 'before_stop'):
            self.plugin.before_stop(self)

    def after_stop(self):
        """
        Post stop callback.
        """
        if hasattr(self.plugin, 'after_stop'):
            self.plugin.after_stop(self)

    def get_cmd(self):
        """
        To get cmd string for run.
        """
        return compile_cmd(
            client_cmd=self.cmd,
            cmd_prefix=self.cmd_prefix,
            daemon_bin=self.daemon_bin,
            cmd_options=self.cmd_args,
        )

    def add_cmd_option(self, opt, value=None):
        """
        Add option to cmd.
        """
        self.cmd_args.add_option(opt, value=value)

    def get_cmd_option(self, opt, default=None):
        """
        To get cmd option.
        """
        return self.cmd_args.get_option(opt, default=default)

    def start(self, **kwargs):
        """
        Start daemon.

        :param kwargs: subprocess.Popen kwargs
        """
        if not self.process and self.pid_file.exist:
            self.pid_file.remove()
            logger.warning('Old pid file "%s" was removed', self.pid_file.path)

        if self.started:
            return

        logger.debug('Daemod "%s" start', self.name)

        self.before_start()

        cmd = self.get_cmd()
        process_options = self.process_options.copy()

        if self.stdout:
            process_options.update(stdout=open(self.stdout, 'a'))
        if self.stderr:
            process_options.update(stderr=open(self.stderr, 'a'))
        if kwargs:
            process_options.update(kwargs)

        process_options.update(shell=True)

        logger.debug(
            'Daemon "{}" cmd: "{}" process_options: {}'.format(
                self.name, cmd, process_options,
            ),
        )
        self.process = psutil.Popen(cmd, **process_options)

        self.after_start()

    def stop(self, recursive=True):
        """
        Stop daemon.

        :param recursive: if True then to stop children of process
        """
        if self.stopped:
            return

        logger.debug('Daemod "%s" stop', self.name)

        self.before_stop()

        utils.process_terminate_by_pid_file(self.pid_file)
        utils.safe_shot_down(self.process, recursive=recursive)

        self.pid_file.remove()

        self.process = None

        self.after_stop()

    def restart(self):
        """
        Restart daemon
        """
        self.stop()
        self.start()
