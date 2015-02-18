# -*- coding: utf-8 -*-

import logging

import psutil

from noseapp_daemon import utils


logger = logging.getLogger(__name__)


class DaemonInterface(object):
    """
    Интерфейс для управления демоном
    """

    @property
    def name(self):
        """
        Имя демона
        """
        raise NotImplementedError(
            'Property "name" should be implemented in subclasses.',
        )

    @property
    def cmd(self):
        """
        cmd для запуска
        """
        raise NotImplementedError(
            'Property "cmd" should be implemented in subclasses.',
        )

    @property
    def process_options(self):
        """
        Опции для subprocess.Popen
        """
        return {}

    def begin(self):
        """
        Callback вызывается после инициализации класса
        """
        pass

    def finalize(self):
         """
        Callback вызывается перед удалением объекта
        """

    def before_start(self):
        """
        Callback вызывается перед запуском
        """
        pass

    def after_start(self):
        """
        Callback вызывается после запуска
        """
        pass

    def before_stop(self):
        """
        Callback вызывается перед остановкой
        """
        pass

    def after_stop(self):
        """
        Callback вызывается после остановки
        """
        pass


class Daemon(DaemonInterface):
    """
    Базовый класс демона
    """

    def __init__(self, daemon_bin,
                 working_dir=None,
                 client=None,
                 pid_file=None,
                 config_file=None,
                 cmd_prefix=None,
                 stdout=None,
                 stderr=None):
        """
        :param daemon_bin: путь до executable файла
        :param working_dir: путь до рабочей дирректории
        :param client: инстанс клиента
        :param pid_file: путь до pid файла
        :param config_file: путь до конфиг файла
        :param cmd_prefix: префикс к cmd для запуска
        :param stdout: путь до файла куда нужно писать stdout(работает только совместно с cmd_prefix)
        :param stderr: путь до файла куда нужно писать stderr(работает только совместно с cmd_prefix)
        """
        self.daemon_bin = daemon_bin
        self.client = client
        self.pid_file = utils.PidFileObject(pid_file)
        self.config_file = config_file
        self.working_dir = working_dir or '.'

        if cmd_prefix:
            self.cmd_prefix = [c.strip() for c in cmd_prefix.split(' ')]
        else:
            self.cmd_prefix = None

        self.process = None

        self.get_stdout, self.get_stderr = utils.get_std(stdout, stderr, cmd_prefix)

        self.begin()

    def __del__(self):
        self.finalize()

    @property
    def started(self):
        """
        Флаг сигнализирует о том, что демон запущен
        """
        return bool(self.process) or self.pid_file.exist

    @property
    def stopped(self):
        """
        Инверсия флага started
        """
        return not self.started

    def start(self):
        """
        Стартует демона
        """
        if self.started:
            return

        logger.debug('Daemod "%s" start', self.name)

        self.before_start()

        self.process = psutil.Popen(
            self.cmd if not self.cmd_prefix else self.cmd_prefix + self.cmd,
            stderr=self.get_stderr(),
            stdout=self.get_stdout(),
            **self.process_options
        )

        self.after_start()

    def stop(self):
        """
        Останавливает демона
        """
        if self.stopped:
            return

        logger.debug('Daemod "%s" stop', self.name)

        self.before_stop()

        utils.process_terminate_by_pid_file(self.pid_file)

        utils.safe_shot_down(self.process)

        self.pid_file.remove()

        if self.cmd_prefix:
            self.process.communicate()

        self.process = None

        self.after_stop()
