=======
Artisan
=======

.. image:: https://img.shields.io/travis/SethMichaelLarson/artisan/master.svg
    :target: https://travis-ci.org/SethMichaelLarson/artisan
    :alt: Linux and MacOS Build Status
.. image:: https://img.shields.io/appveyor/ci/SethMichaelLarson/artisan/master.svg
    :target: https://ci.appveyor.com/project/SethMichaelLarson/artisan
    :alt: Windows Build Status
.. image:: https://img.shields.io/codecov/c/github/SethMichaelLarson/artisan/master.svg
    :target: https://codecov.io/gh/SethMichaelLarson/artisan
    :alt: Test Suite Coverage
.. image:: https://img.shields.io/codeclimate/github/SethMichaelLarson/artisan.svg
    :target: https://codeclimate.com/github/SethMichaelLarson/artisan
    :alt: Code Health
.. image:: https://pyup.io/repos/github/sethmichaellarson/artisan/shield.svg
     :target: https://pyup.io/repos/github/sethmichaellarson/artisan
     :alt: Dependency Versions
.. image:: https://img.shields.io/pypi/v/artisan.svg
    :target: https://pypi.python.org/pypi/artisan
    :alt: PyPI Version
.. image:: https://img.shields.io/badge/say-thanks-ff69b4.svg
    :target: https://saythanks.io/to/SethMichaelLarson
    :alt: Say Thanks to the Maintainers

About
-----

Providing a platform-agnostic interface for automation, continuous integration, and farm management.

- Generic interface for managing a farm.
- Easily extensible for custom use cases.
- Support for Linux, Mac OS, and Windows servers and workers.
- High code health and test coverage.

License
-------

This module is licensed under the MIT license.

Installation
------------

``$ python -m pip install artisan``

Usage
-----
.. code-block:: python
    
    from artisan.worker import WorkerPool, LocalWorker
    
    # Create a pool to manage workers.
    # The workers for this pool only work on the local machine.
    pool = WorkerPool(10, worker_factory=lambda: LocalWorker())
    
    # Wait for a worker to become available (Timeout in 1 second).
    worker = pool.acquire(timeout=1.0)
    if not worker:
        pass  # Do stuff here if a worker isn't available (timeout, closed pool...).
        
    # Otherwise we're free to use our worker.
    print(worker)
    
    # Execute a command on the worker.
    command = worker.execute("echo 'Hello, world!'")
    command.wait(timeout=0.1)  # Wait for it with a timeout.
    print(command.exit_status)
    print(command.stdout)
    
    # Move the current working directory.
    print(worker.cwd)
    worker.chdir("..")
    print(worker.cwd)
    
    # List files and folders in the current working directory.
    print(worker.listdir())
    
    # Access and change the worker's environment.
    print(worker.environ["HOME"])
    worker.environ["ARTISAN"] = "Artisan <3 Automation"
    command = worker.execute("echo '$ARTISAN'")
    command.wait(timeout=0.1)
    print(command.stdout)
    
    # Does the worker have access to Python?
    print(worker.python_version_info)
    
    # Run a Python script on the worker.
    command = worker.python("import sys; sys.stdout.write('Called from Python!')")
    command.wait(0.1)
    print(command.stdout)
    
    # Release the worker back into the pool.
    pool.release(worker)

Contributing
------------
This repository is thankful for all community-made PRs and Issues. :)

If this work is useful to you, `feel free to say thanks <https://saythanks.io/to/SethMichaelLarson>`_, takes only a little time and really brightens my day! :cake:

Artisan :heart: Automation
    
