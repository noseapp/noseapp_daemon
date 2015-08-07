# -*- coding: utf-8 -*-

from unittest import TestCase

from noseapp_daemon import runner

from .daemon import TestService


class TestDaemonService(TestCase):

    def test_create_service(self):
        service = TestService()
        self.assertTrue(hasattr(service, 'daemon'))
        self.assertIsInstance(service.daemon, runner.DaemonRunner)

        service.start()
        self.assertTrue(service.daemon.started)
        self.assertFalse(service.daemon.is_dead)

        service.stop()
        self.assertTrue(service.daemon.stopped)
        self.assertTrue(service.daemon.is_dead)

    def test_init_config(self):
        service = TestService(config=dict())
        self.assertIsInstance(service.config, dict)

    def test_init_options(self):
        service = TestService(options=dict())
        self.assertIsInstance(service.options, dict)
