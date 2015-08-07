# -*- coding: utf-8 -*-

from unittest import TestCase
from collections import OrderedDict

from noseapp_daemon import runner
from noseapp_daemon import management

from .daemon import TestService
from .daemon import create_fake_daemon


class TestDaemonManagement(TestCase):

    def test_add_service(self):
        m = management.DaemonManagement()
        m.add_service(TestService())

        self.assertIsInstance(m.service(TestService.name), TestService)

    def test_add_daemon(self):
        m = management.DaemonManagement()
        m.add_daemon(create_fake_daemon('test'))

        self.assertIsInstance(m.daemon('test'), runner.DaemonRunner)

    def test_checkout_service(self):
        m = management.DaemonManagement()
        m.add_service(TestService())

        with m.checkout_service(TestService.name) as service:
            self.assertIsInstance(service, TestService)
            service.start()
            self.assertTrue(service.daemon.started)
            service.stop()
            self.assertTrue(service.daemon.stopped)

    def test_checkout_daemon(self):
        m = management.DaemonManagement()
        m.add_daemon(create_fake_daemon('test'))

        with m.checkout_daemon('test') as daemon:
            self.assertIsInstance(daemon, runner.DaemonRunner)
            daemon.start()
            self.assertTrue(daemon.started)
            daemon.stop()
            self.assertTrue(daemon.stopped)

    def test_start_stop_all(self):
        m = management.DaemonManagement()

        m.add_service(TestService())
        m.add_daemon(create_fake_daemon('test'))

        daemon = m.daemon('test')
        service = m.service(TestService.name)

        m.start_all()
        self.assertTrue(daemon.started)
        self.assertTrue(service.daemon.started)

        m.stop_all()
        self.assertTrue(daemon.stopped)
        self.assertTrue(service.daemon.stopped)

    def test_start_stop_services_and_daemons(self):
        m = management.DaemonManagement()

        m.add_service(TestService())
        m.add_daemon(create_fake_daemon('test'))

        daemon = m.daemon('test')
        service = m.service(TestService.name)

        m.start_services()
        self.assertTrue(service.daemon.started)
        self.assertFalse(daemon.started)

        m.stop_services()
        self.assertTrue(service.daemon.stopped)
        self.assertFalse(daemon.started)

        m.start_daemons()
        self.assertFalse(service.daemon.started)
        self.assertTrue(daemon.started)

        m.stop_daemons()
        self.assertFalse(service.daemon.started)
        self.assertTrue(daemon.stopped)

    def test_services_property(self):
        service = TestService()
        m = management.DaemonManagement()
        m.add_service(service)

        self.assertIsInstance(m.services, OrderedDict)
        self.assertIn(service.name, m.services)

    def test_daemons_property(self):
        daemon = create_fake_daemon('test')
        m = management.DaemonManagement()
        m.add_daemon(daemon)

        self.assertIsInstance(m.daemons, OrderedDict)
        self.assertIn(daemon.name, m.daemons)
