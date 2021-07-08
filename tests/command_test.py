import unittest
import suntest.core.command as Command


class TestCommand(unittest.TestCase):
    def test_execute_command_ok(self):
        who_execute_command = ["who"]

        self.assertTrue(Command.execute_command(who_execute_command))

    def test_execute_command_OSError(self):
        unknow_execute_command = ["unknow"]

        with self.assertRaises(OSError):
            Command.execute_command(unknow_execute_command)

    def test_execute_command_command_type_error(self):
        who_shell_command = "who"

        with self.assertRaises(TypeError):
            Command.execute_command(who_shell_command)

    def test_execute_command_timeout_type_error(self):
        who_execute_command = ["who"]
        timeout = str("30")

        with self.assertRaises(TypeError):
            Command.execute_command(who_execute_command, timeout)

    def test_execute_command_timeout(self):
        sleep_command = ["sleep", "30"]
        timeout = 10

        self.assertFalse(Command.execute_command(sleep_command, timeout))

    def test_shell_command_ok(self):
        who_shell_command = "who"

        self.assertTrue(Command.shell_command(who_shell_command))

    def test_shell_command_OSError(self):
        unknow_shell_command = "unknow"

        self.assertFalse(Command.shell_command(unknow_shell_command))

    def test_shell_command_command_type_error(self):
        who_execute_command = ["who"]

        with self.assertRaises(TypeError):
           Command.shell_command(who_execute_command)

    def test_shell_command_timeout_type_error(self):
        who_shell_command = "who"

        with self.assertRaises(TypeError):
            Command.shell_command(who_shell_command, timeout=str("0"))

    def test_shell_command_timeout(self):
        sleep_shell_command = "sleep 30"

        self.assertFalse(Command.shell_command(sleep_shell_command, timeout=10))
