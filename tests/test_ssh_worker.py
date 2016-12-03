import getpass
import os
import sys
import time
from artisan.worker import SshWorker, SshCommand

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
try:
    from time import monotonic
except ImportError:
    from time import time as monotonic


def _safe_close(worker):
    try:
        worker.close()
    except Exception:
        pass


@unittest.skipUnless("ARTISAN_SSH_PASSWORD" in os.environ, ("Set the environment variable ARTISAN_SSH_PASSWORD"
                                                            " to be able to test the SshWorker tests."))
class TestSshWorker(unittest.TestCase):
    def make_worker(self):
        worker = SshWorker("localhost", getpass.getuser(), password=os.environ["ARTISAN_SSH_PASSWORD"])
        self.addCleanup(_safe_close, worker)
        return worker

    def test_execute_command_type(self):
        worker = self.make_worker()
        self.assertIsInstance(worker.execute('Hello'), SshCommand)

    def test_execute_multiple(self):
        commands = []
        worker = self.make_worker()
        start_time = monotonic()
        commands.append(worker.execute("sleep 1"))
        for command in commands:
            command.wait(timeout=2.0)
        end_time = monotonic()
        self.assertLessEqual(end_time - start_time, 10.0)

    def test_stdout(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stdout.write('Hello')\"")
        command.wait(0.1)
        self.assertEqual(command.stdout.strip(), b'Hello')
        self.assertEqual(command.stderr, b'')
        self.assertEqual(command.exit_status, 0)

    def test_stderr(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stderr.write('Hello')\"")
        command.wait(0.1)
        self.assertEqual(command.stderr.strip(), b'Hello')
        self.assertEqual(command.stdout, b'')
        self.assertEqual(command.exit_status, 0)

    def test_exit_status(self):
        worker = self.make_worker()
        for exit_status in range(10):
            command = worker.execute(sys.executable + " -c \"import sys; sys.exit(%s)\"" % str(exit_status))
            command.wait(0.1)
            self.assertEqual(command.exit_status, exit_status)

    @unittest.skipIf(sys.version_info <= (3, 0, 0), ("subprocess.Popen.poll() waits until"
                                                     "process is complete on Python 2.x"))
    def test_exit_time(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.exit(2)\"")
        self.assertEqual(command.exit_status, None)
        time.sleep(1.0)
        self.assertEqual(command.exit_status, 2)

    def test_cancel_command(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.stdout.write('Hello')\"")
        time.sleep(0.1)
        command.cancel()
        self.assertIs(command.exit_status, None)
        self.assertEqual(command.stdout, b'')
        self.assertEqual(command.stderr, b'')

    def test_close_worker(self):
        worker = self.make_worker()
        command = worker.execute("sleep 1")
        worker.close()
        self.assertTrue(worker.closed)
        self.assertTrue(command.cancelled)

    def test_worker_already_closed(self):
        worker = self.make_worker()
        worker.close()
        self.assertRaises(ValueError, worker.close)

    def test_command_already_cancelled(self):
        worker = self.make_worker()
        command = worker.execute("sleep 1")
        command.cancel()
        self.assertRaises(ValueError, command.cancel)

    def test_read_after_exit(self):
        worker = self.make_worker()
        command = worker.execute("echo Hello")
        command.wait(0.1)
        self.assertEqual(command.stdout.strip(), b'Hello')

    def test_cwd(self):
        cwd = os.getcwd()
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.getcwd())\"")
        command.wait()
        self.assertEqual(cwd, str(command.stdout).replace("\\\\", "\\").strip("b'\""))

    def test_chdir(self):
        cwd = os.path.dirname(os.getcwd())
        worker = self.make_worker()
        worker.chdir(cwd)
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.getcwd())\"")
        command.wait()
        self.assertEqual(cwd, str(command.stdout).replace("\\\\", "\\").strip("b'\""))

    def test_chdir_same_directory(self):
        same_dir = os.getcwd()
        worker = self.make_worker()
        worker.chdir(".")
        self.assertEqual(same_dir, worker.cwd)

    def test_chdir_parent_directory(self):
        parent_dir = os.path.dirname(os.getcwd())
        worker = self.make_worker()
        worker.chdir("..")
        self.assertEqual(parent_dir, worker.cwd)

    def test_environ_get(self):
        worker = self.make_worker()
        for key, val in os.environ.items():
            self.assertIn(key, worker.environ)
            self.assertEqual(worker.environ[key], val)

    def test_environ_set(self):
        worker = self.make_worker()
        worker.environ["ENVIRONMENT"] = "VARIABLE"
        self.assertIn("ENVIRONMENT", worker.environ)
        self.assertEqual(worker.environ["ENVIRONMENT"], "VARIABLE")

    def test_environ_in_commands(self):
        worker = self.make_worker()
        worker.environ["ENVIRONMENT"] = "VARIABLE"
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"")
        command.wait(0.1)
        self.assertEqual(command.stdout.strip(), b'VARIABLE')

    def test_listdir(self):
        expected = sorted(os.listdir("."))
        worker = self.make_worker()
        self.assertEqual(sorted(worker.listdir()), expected)
