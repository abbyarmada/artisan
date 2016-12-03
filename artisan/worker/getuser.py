""" Cross-platform way to access the name of
the local user. Tries it's best to get the name
of the current user running the program. """

import os
import sys

__all__ = ["getuser"]
__author__ = "Seth Michael Larson <sethmichaellarson@protonmail.com>"
__license__ = """

MIT License

Copyright (c) 2016 Seth Michael Larson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


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
