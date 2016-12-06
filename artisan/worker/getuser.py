""" Cross-platform way to access the name of
the local user. Tries it's best to get the name
of the current user running the program. """

import os
import sys


def getuser():
    """ Get the name of the current user from
    a variety of sources from the most reliable
    sources to least. """
    if sys.platform.startswith("win32"):
        try:  # Platform-specific: Windows
            import win32api
            return win32api.GetUserName()
        except ImportError:
            pass

    # Linux only.
    try:
        import pwd
        return pwd.getpwuid(os.getuid())[0]
    except Exception:
        pass

    # Linux only.
    if hasattr(os, "getlogin"):
        return os.getlogin()

    # Only looks at environment variables.
    try:
        import getpass
        return getpass.getuser()
    except Exception:
        pass

    # Username could not be determined.
    return "<unknown>"
