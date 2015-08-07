# -*- coding: utf-8 -*-

import os
import errno
import signal
import socket
import logging
from random import Random
from collections import Iterator

import psutil


logger = logging.getLogger(__name__)


def safe_shot_down(process, recursive=True):
    """
    :type process: psutil.Popen
    """
    if recursive:
        children = (c for c in process.children(recursive=True))
        for ch in children:
            safe_shot_down(ch, recursive=False)

    try:
        process.terminate()
        process.wait()
    except (psutil.NoSuchProcess, OSError, AttributeError):
        pass


def kill_process_by_pid(pid):
    """
    :param pid: pid of process
    :type pid: int
    """
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass


def process_terminate_by_pid_file(pid_file):
    """
    :type pid_file: PidFileObject
    """
    if pid_file.exist:
        kill_process_by_pid(pid_file.pid)


class PidFileObject(object):

    def __init__(self, file_path):
        """
        :param file_path: pid file path
        """
        self._file_path = file_path

    @property
    def exist(self):
        try:
            return os.path.isfile(self._file_path)
        except TypeError:
            return False

    @property
    def path(self):
        return self._file_path

    @property
    def pid(self):
        if not self._file_path:
            return None

        try:
            with open(self._file_path) as fp:
                return int(fp.readline().strip())
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise
        except ValueError:
            pass

        return None

    def remove(self):
        if self.exist:
            try:
                os.unlink(self._file_path)
            except OSError:
                pass

    def __repr__(self):
        return '<PidFile {}>'.format(self._file_path)


def which(command, default=''):
    """
    Get full path to bin file by command name
    """
    is_bin = lambda p: os.path.isfile(p) and os.access(p, os.X_OK)

    if is_bin(default):
        return default

    for path in os.environ['PATH'].split(os.pathsep):
        bin_file = os.path.join(path, command)
        if is_bin(bin_file):
            return bin_file

    return None


def port_is_free(port):
    """
    Check port is freedom
    """
    localhost = '127.0.0.1'

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    result = sock.connect_ex(
        (localhost, port),
    )
    sock.close()

    return bool(result)


class RandomizePort(Iterator):
    """
    To get randomize port.

    Usage:
        port = RandomizePort.get()
    """

    memo = set()
    random = None

    MIN_PORT = 61001
    MAX_PORT = 65535
    MAX_PORTS = (MAX_PORT - MIN_PORT) / 30

    def __init__(self):
        if not self.random:
            self.random = Random()
        self.__port = self.random.randint(self.MIN_PORT, self.MAX_PORT)

    @classmethod
    def init_sid(cls, sid):
        cls.random = Random(sid)

    def next(self):
        while self.__port in self.memo and not port_is_free(self.__port):

            if len(self.memo) >= self.MAX_PORTS:
                raise StopIteration

            self.__port = self.random.randint(self.MIN_PORT, self.MAX_PORT)

        self.memo.add(self.__port)

        return self.__port

    @classmethod
    def get(cls):
        return cls().next()
