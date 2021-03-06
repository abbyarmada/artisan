import os
import sys
import tempfile
import time

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


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


class _BaseWorkerTestCase(object):
    COMMAND_TYPE = None

    def make_worker(self):
        raise NotImplementedError()

    def test_execute_command_type(self):
        worker = self.make_worker()
        self.assertIsInstance(worker.execute('Hello'), self.COMMAND_TYPE)

    def test_execute_async(self):
        worker = self.make_worker()
        start_time = monotonic()
        worker.execute("sleep 1")
        end_time = monotonic()
        self.assertLess(end_time - start_time, 1.0)

    def test_execute_multiple(self):
        commands = []
        worker = self.make_worker()
        start_time = monotonic()
        for _ in range(3):
            commands.append(worker.execute(sys.executable + " -c \"import time; time.sleep(1.0)\""))
        for command in commands:
            command.wait(timeout=1.5)
        end_time = monotonic()
        for command in commands:
            self.assertEqual(command.exit_status, 0)
        self.assertLessEqual(end_time - start_time, 3.0)

    def test_execute_supply_environment(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"",
                                 environment={"ENVIRONMENT": "VARIABLE"})
        command.wait(1.0)
        print(command.exit_status)
        print(command.stderr)
        self.assertEqual(command.stdout, b'VARIABLE')

    def test_execute_override_environment(self):
        worker = self.make_worker()
        worker.environ["ENVIRONMENT"] = "VARIABLE1"
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.environ['ENVIRONMENT'])\"",
                                 environment={"ENVIRONMENT": "VARIABLE2"})
        command.wait(1.0)
        self.assertEqual(command.stdout, b'VARIABLE2')

    def test_stdout(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stdout.write('Hello')\"")
        command.wait(0.1)
        self.assertEqual(command.stdout, b'Hello')
        self.assertEqual(command.stderr, b'')
        self.assertEqual(command.exit_status, 0)

    def test_stderr(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys; sys.stderr.write('Hello')\"")
        command.wait(0.1)
        self.assertEqual(command.stderr, b'Hello')
        self.assertEqual(command.stdout, b'')
        self.assertEqual(command.exit_status, 0)

    def test_exit_status(self):
        worker = self.make_worker()
        for exit_status in range(10):
            command = worker.execute(sys.executable + " -c \"import sys; sys.exit(%s)\"" % str(exit_status))
            command.wait(1.0)
            self.assertEqual(command.exit_status, exit_status)

    @unittest.skipIf(sys.version_info <= (3, 0, 0), ("subprocess.Popen.poll() waits until"
                                                     "process is complete on Python 2.x"))
    def test_exit_time(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.exit(2)\"")
        self.assertEqual(command.exit_status, None)
        time.sleep(1.0)
        self.assertEqual(command.exit_status, 2)

    @unittest.skipIf(sys.version_info <= (3, 0, 0), ("subprocess.Popen.poll() waits until"
                                                     "process is complete on Python 2.x"))
    def test_wait_timeout(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.5); sys.exit(2)\"")
        command.wait(0.1)
        self.assertIs(command.exit_status, None)
        command.wait(0.5)
        self.assertEqual(command.exit_status, 2)

    def test_cancel_command(self):
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(0.3); sys.stdout.write('Hello')\"")
        time.sleep(0.1)
        command.cancel()
        self.assertIs(command.exit_status, None)
        self.assertEqual(command.stdout, b'')
        self.assertEqual(command.stderr, b'')

    def test_command_callbacks(self):
        array = []
        worker = self.make_worker()
        command = worker.execute(sys.executable + " -c \"import sys, time; time.sleep(1.0);\"")

        def callback(cmd):
            self.assertIs(cmd, command)
            array.append(1)

        command.add_callback(callback)
        command.wait(1.0)
        self.assertIn(1, array)

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

    def test_chdir(self):
        cwd = os.getcwd()
        worker = self.make_worker()
        worker.change_directory(cwd)
        command = worker.execute(sys.executable + " -c \"import os, sys; sys.stdout.write(os.getcwd())\"")
        command.wait(0.1)
        self.assertEqual(cwd, str(command.stdout).replace("\\\\", "\\").strip("b'\""))

    def test_chdir_same_directory(self):
        same_dir = os.getcwd()
        worker = self.make_worker()
        worker.change_directory(same_dir)
        worker.change_directory(".")
        self.assertEqual(same_dir, worker.cwd)

    def test_chdir_parent_directory(self):
        parent_dir = os.path.dirname(os.getcwd())
        worker = self.make_worker()
        worker.change_directory(os.getcwd())
        worker.change_directory("..")
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
        worker.change_directory(os.getcwd())
        self.assertEqual(sorted(worker.list_directory()), expected)

    def test_listdir_give_path(self):
        expected = sorted(os.listdir("."))
        worker = self.make_worker()
        self.assertEqual(sorted(worker.list_directory(path=os.getcwd())), expected)

    def test_open_file(self):
        worker = self.make_worker()
        self.addCleanup(_safe_remove, "tmp")
        _safe_remove("tmp")
        with worker.open_file("tmp", mode="w") as f:
            f.write("Hello, world!")
        with worker.open_file("tmp", mode="r") as f:
            self.assertEqual(f.read(), "Hello, world!")

    def test_changing_cwd(self):
        worker = self.make_worker()
        cwd = os.getcwd()
        self.addCleanup(os.chdir, cwd)
        os.chdir("..")
        self.assertEqual(worker.cwd, cwd)

    def test_put_file(self):
        worker = self.make_worker()
        self.addCleanup(_safe_remove, "tmp1")
        self.addCleanup(_safe_remove, "tmp2")
        _safe_remove("tmp1")
        _safe_remove("tmp2")
        with worker.open_file("tmp1", mode="w") as f:
            f.write("put")

        self.assertTrue(os.path.isfile("tmp1"))
        self.assertFalse(os.path.isfile("tmp2"))

        worker.put_file("tmp1", "tmp2")

        self.assertFalse(os.path.isfile("tmp1"))
        self.assertTrue(os.path.isfile("tmp2"))

        with worker.open_file("tmp2", mode="r") as f:
            self.assertEqual(f.read(), "put")

    def test_get_file(self):
        worker = self.make_worker()
        self.addCleanup(_safe_remove, "tmp1")
        self.addCleanup(_safe_remove, "tmp2")
        _safe_remove("tmp1")
        _safe_remove("tmp2")
        with worker.open_file("tmp1", mode="w") as f:
            f.write("get")

        self.assertTrue(os.path.isfile("tmp1"))
        self.assertFalse(os.path.isfile("tmp2"))

        worker.get_file("tmp1", "tmp2")

        self.assertFalse(os.path.isfile("tmp1"))
        self.assertTrue(os.path.isfile("tmp2"))

        with worker.open_file("tmp2", mode="r") as f:
            self.assertEqual(f.read(), "get")

    def test_stat(self):
        worker = self.make_worker()
        self.addCleanup(_safe_remove, "tmp1")
        _safe_remove("tmp1")

        with worker.open_file("tmp1", mode="w") as f:
            f.write("Hello, world!")

        file_attrs = worker.stat_file("tmp1", follow_symlinks=False)
        self.assertEqual(file_attrs.st_size, 13)

    @unittest.skipIf(sys.platform == "win32", "Windows doesn't implement symbolic links.")
    def test_stat_follow_symlinks(self):
        worker = self.make_worker()
        self.addCleanup(_safe_remove, "tmp1")
        self.addCleanup(_safe_remove, "tmp2")
        _safe_remove("tmp1")
        _safe_remove("tmp2")

        with worker.open_file("tmp2", mode="w") as f:
            f.write("Hello, world!")
        os.symlink("tmp2", "tmp1")

        file_attrs = worker.stat_file("tmp1")
        self.assertEqual(file_attrs.st_size, 13)

    def test_find_python_executable(self):
        worker = self.make_worker()
        self.assertIsNot(worker.python_executable, None)

    def test_python_version(self):
        worker = self.make_worker()
        worker._python_executable = sys.executable
        self.assertEqual(worker.python_version, tuple(sys.version_info)[:3])

    def test_execute_python_stdout(self):
        worker = self.make_worker()
        command = worker.execute_python("import sys; sys.stdout.write('Hello, world!')")
        command.wait(1.0)
        self.assertEqual(command.stdout, b'Hello, world!')

    def test_execute_python_stderr(self):
        worker = self.make_worker()
        command = worker.execute_python("import sys; sys.stderr.write('Hello, world!')")
        command.wait(1.0)
        self.assertEqual(command.stderr, b'Hello, world!')

    def test_execute_python_exit_code(self):
        worker = self.make_worker()
        for exit_status in range(10):
            command = worker.execute_python("import sys; sys.exit(%s)" % exit_status)
            command.wait(1.0)
            self.assertEqual(command.exit_status, exit_status)

    def test_exeucte_python_multiple_lines(self):
        worker = self.make_worker()
        code = """
import sys
sys.stdout.write('Hello, world!')
"""
        command = worker.execute_python(code)
        command.wait(1.0)
        self.assertEqual(command.stdout, b'Hello, world!')

    def test_tempdir(self):
        worker = self.make_worker()
        self.assertEqual(worker.tmp_directory, tempfile.gettempdir())
        self.assertTrue(worker.is_directory(worker.tmp_directory))
