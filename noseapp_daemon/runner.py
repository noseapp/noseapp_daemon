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


class DaemonRunner(object):
    """
    Base class for daemon run
    """

    DAEMON_BIN = None

    config_class = None

    def __init__(self,
                 daemon_bin=None,
                 stdout=None,
                 stderr=None,
                 pid_file=None,
                 cmd_prefix=None,
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
        :param options: will be using like options property
        """
        self.options = options
        self.cmd_args = CmdArgs()
        self.cmd_prefix = cmd_prefix
        self.pid_file = utils.PidFileObject(pid_file)
        self.daemon_bin = daemon_bin or self.DAEMON_BIN

        self.config = None
        self.process = None

        self.stdout = stdout
        self.stderr = stderr

        if self.config_class:
            self.config = self.config_class(self)

        self.setup()

        if not isinstance(self.daemon_bin, basestring) or not os.path.exists(self.daemon_bin):
            raise DaemonError(
                '"{}" bin file is not found'.format(self.name),
            )

    def name(self):
        """
        Name of daemon
        """
        raise NotImplementedError(
            'Property "name" should be implemented in subclasses.',
        )

    def setup(self):
        """
        Will be called after initialization
        """
        pass

    @property
    def cmd(self):
        """
        Define your own command line

        :return: list, tuple, str
        """
        return None

    @property
    def process_options(self):
        """
        Arguments for Popen __init__ method
        """
        return {}

    @property
    def started(self):
        return bool(self.process) or self.pid_file.exist

    @property
    def stopped(self):
        return not self.started

    def before_start(self):
        """
        Pre start callback
        """
        if hasattr(self.config, 'before_start'):
            self.config.before_start()

    def after_start(self):
        """
        Post start callback
        """
        if hasattr(self.config, 'after_start'):
            self.config.after_start()

    def before_stop(self):
        """
        Pre stop callback
        """
        if hasattr(self.config, 'before_stop'):
            self.config.before_stop()

    def after_stop(self):
        """
        Post stop callback
        """
        if hasattr(self.config, 'after_stop'):
            self.config.after_stop()

    def get_cmd(self):
        """
        Get string of running
        """
        return compile_cmd(
            client_cmd=self.cmd,
            cmd_prefix=self.cmd_prefix,
            daemon_bin=self.daemon_bin,
            cmd_options=self.cmd_args,
        )

    def add_cmd_option(self, opt, value=None):
        """
        Add option to cmd
        """
        self.cmd_args.add_option(opt, value=value)

    def get_cmd_option(self, opt, default=None):
        """
        Get cmd option
        """
        return self.cmd_args.get_option(opt, default=default)

    def start(self, **kwargs):
        """
        Start daemon
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

    def stop(self):
        """
        Stop daemon
        """
        if self.stopped:
            return

        logger.debug('Daemod "%s" stop', self.name)

        self.before_stop()

        utils.process_terminate_by_pid_file(self.pid_file)
        utils.safe_shot_down(self.process, recursive=True)

        self.pid_file.remove()

        self.process = None

        self.after_stop()
