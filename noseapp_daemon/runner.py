# -*- coding: utf-8 -*-

import logging
from subprocess import PIPE

import psutil

from noseapp_daemon import utils


logger = logging.getLogger(__name__)


class CallbackInterface(object):
    """
    Callback methods for daemon management
    """

    @property
    def process_options(self):
        """
        Arguments for Popen __init__ method
        """
        return {}

    def setup(self):
        """
        Be called after initialization
        """
        pass

    def before_start(self):
        """
        Pre start callback
        """
        pass

    def after_start(self):
        """
        Post start callback
        """
        pass

    def before_stop(self):
        """
        Pre stop callback
        """
        pass

    def after_stop(self):
        """
        Post stop callback
        """
        pass


class DaemonRunner(CallbackInterface):
    """
    Base class for daemon run
    """

    def __init__(self,
                 daemon_bin=None,
                 stdout=None,
                 stderr=None,
                 pid_file=None,
                 cmd_prefix=None,
                 **options):
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
        """
        self.daemon_bin = daemon_bin
        self.pid_file = utils.PidFileObject(pid_file)
        self.options = options

        if isinstance(cmd_prefix, basestring):
            self.cmd_prefix = [c.strip() for c in cmd_prefix.split(' ')]
        else:
            self.cmd_prefix = cmd_prefix

        self.process = None

        self.stdout = stdout
        self.stderr = stderr

        self.setup()

    @property
    def name(self):
        raise NotImplementedError(
            'Property "name" should be implemented in subclasses.',
        )

    @property
    def cmd(self):
        raise NotImplementedError(
            'Property "cmd" should be implemented in subclasses.',
        )

    @property
    def started(self):
        return bool(self.process) or self.pid_file.exist

    @property
    def stopped(self):
        return not self.started

    def start(self):
        """
        Start daemon
        """
        if not self.process and self.pid_file.exist:
            self.pid_file.remove()

        if self.started:
            return

        logger.debug('Daemod "%s" start', self.name)

        self.before_start()

        self.process = psutil.Popen(
            self.cmd if not self.cmd_prefix else self.cmd_prefix + self.cmd,
            stderr=PIPE,
            stdout=PIPE,
            **self.process_options
        )

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
        utils.safe_shot_down(self.process)

        self.pid_file.remove()

        if self.stdout:
            with open(self.stdout, 'a') as stdout:
                for line in self.process.stdout:
                    stdout.write(line)

        if self.stderr:
            with open(self.stderr, 'a') as stderr:
                for line in self.process.stderr:
                    stderr.write(line)

        self.process = None

        self.after_stop()
