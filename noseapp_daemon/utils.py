# -*- coding: utf-8 -*-

import os
import errno
import signal
import logging

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


def which(program_name, default=''):
    is_bin = lambda p: os.path.isfile(p) and os.access(p, os.X_OK)

    if is_bin(default):
        return default

    for path in os.environ['PATH'].split(os.pathsep):
        bin_file = os.path.join(path, program_name)
        if is_bin(bin_file):
            return bin_file

    return None
