# -*- coding: utf-8 -*-

from unittest import TestCase

from noseapp_daemon import utils
from noseapp_daemon import runner

from .daemon import create_fake_daemon


class TestDaemonRunner(TestCase):

    def test_compile_cmd(self):
        expect_cmd = 'prefix daemon_bin --help=me -h'

        cmd_options = runner.CmdArgs()
        cmd_options.add_option('--help', 'me')
        cmd_options.add_option('-h')
        fake_cmd = runner.compile_cmd(
            cmd_prefix='prefix',
            daemon_bin='daemon_bin',
            cmd_options=cmd_options,
        )
        self.assertEqual(fake_cmd, expect_cmd)

        fake_cmd = runner.compile_cmd(client_cmd=expect_cmd)
        self.assertEqual(fake_cmd, expect_cmd)

        fake_cmd = runner.compile_cmd(
            client_cmd=(
                'prefix',
                'daemon_bin',
                '--help=me',
                '-h',
            ),
        )
        self.assertEqual(fake_cmd, expect_cmd)

    def test_cmd_args(self):
        expect_cmd_args = '--help=me --hello'
        cmd_args = runner.CmdArgs()
        cmd_args.add_option('--help', 'me')
        cmd_args.add_option('--hello')

        self.assertEqual(cmd_args.get_option('--help'), 'me')
        self.assertEqual(cmd_args.get_option('--hello'), None)
        self.assertEqual(cmd_args.to_string(), expect_cmd_args)

    def test_daemon_exc(self):
        exc = runner.DaemonError()

        self.assertNotIsInstance(exc, Exception)
        self.assertIsInstance(exc, BaseException)

    def test_daemon_name(self):
        name = 'test_daemon'
        daemon = runner.DaemonRunner(
            name=name,
            daemon_bin=utils.which('ls', default='/bin/ls'),
        )
        self.assertEqual(daemon.name, name)

    def test_bin_is_not_found(self):
        self.assertRaises(runner.DaemonError, runner.DaemonRunner, daemon_bin='not_bin')

    def test_daemon_plugin(self):
        fake_daemon = object()
        plugin = runner.DaemonPlugin()

        self.assertTrue(hasattr(plugin, 'init'))
        self.assertTrue(hasattr(plugin, 'before_start'))
        self.assertTrue(hasattr(plugin, 'after_start'))
        self.assertTrue(hasattr(plugin, 'before_stop'))
        self.assertTrue(hasattr(plugin, 'after_stop'))

        try:
            plugin.init(fake_daemon)
            plugin.after_stop(fake_daemon)
            plugin.after_start(fake_daemon)
            plugin.before_stop(fake_daemon)
            plugin.before_start(fake_daemon)
        except TypeError:
            raise self.failureException('Bad signature of callback method')

    def test_plugin_class(self):
        class FakePluginClass(runner.DaemonPlugin):

            def __init__(self):
                self.counter = 0

            def incr(self):
                self.counter += 1

            def init(self, daemon):
                self.incr()

            def before_start(self, daemon):
                self.incr()

            def after_start(self, daemon):
                self.incr()

            def before_stop(self, daemon):
                self.incr()

            def after_stop(self, daemon):
                self.incr()

        daemon = create_fake_daemon(
            plugin=FakePluginClass(),
        )
        self.assertIsInstance(daemon.plugin, FakePluginClass)
        self.assertEqual(daemon.plugin.counter, 1)

        daemon.start()
        self.assertEqual(daemon.plugin.counter, 3)

        daemon.stop()
        self.assertEqual(daemon.plugin.counter, 5)

        daemon = runner.DaemonRunner(
            daemon_bin=utils.which('ls', default='/bin/ls'),
        )
        self.assertIsInstance(daemon.plugin, runner.DaemonPlugin)

    def test_start_stop_daemon(self):
        daemon = create_fake_daemon()

        daemon.start()
        self.assertTrue(daemon.started)
        self.assertFalse(daemon.is_dead)

        daemon.stop()
        self.assertTrue(daemon.stopped)
        self.assertTrue(daemon.is_dead)

    def test_init_options(self):
        daemon = create_fake_daemon(
            options=dict(),
        )
        self.assertIsInstance(daemon.options, dict)
