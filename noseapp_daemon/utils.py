# -*- coding: utf-8 -*-

import os
import errno
import signal
import logging

import psutil

from noseapp.utils.common import waiting_for
from noseapp.utils.common import TimeoutException


logger = logging.getLogger(__name__)


TIMEOUT = 3.0
WAIT_SLEEP = 1.0


def safe_shot_down(process):
    """
    Безопастно тушит процесс и всех потомков

    :type process: psutil.Popen
    """
    try:

        try:
            children = (c for c in process.children(recursive=True))
            map(safe_shot_down, children)
        except AttributeError:
            pass

        process.terminate()

        try:
            waiting_for(
                process.poll,
                timeout=TIMEOUT,
                sleep=WAIT_SLEEP,
            )
        except TimeoutException:
            process.kill()

    except (psutil.NoSuchProcess, OSError):
        pass


def process_terminate_by_pid_file(pid_file):
    """
    Завершить процесс по pid файлу

    :type pid_file: PidFileObject
    """
    if not pid_file.exist:
        return

    try:
        os.kill(pid_file.pid, signal.SIGTERM)
    except OSError:
        pass


class PidFileObject(object):
    """
    Класс реализует интерфейс для работы с pid файлом
    """

    def __init__(self, file_path):
        self.file_path = file_path

    @property
    def exist(self):
        try:
            return os.path.isfile(self.file_path)
        except TypeError:
            return False

    @property
    def path(self):
        return self.file_path

    @property
    def pid(self):
        if not self.file_path:
            return None

        try:
            with open(self.file_path) as fp:
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
                os.unlink(self.file_path)
            except OSError:
                pass

    def __repr__(self):
        return '<PidFile {}>'.format(self.file_path)
