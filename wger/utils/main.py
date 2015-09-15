# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import sys
import time
import logging
import threading
import webbrowser
import os
import ctypes
import socket

import django

logger = logging.getLogger(__name__)


def get_user_data_path(*args):
    if sys.platform == "win32":
        return win32_get_app_data_path(*args)

    data_home = os.environ.get(
        'XDG_DATA_HOME', os.path.join(
            os.path.expanduser('~'), '.local', 'share'))

    return os.path.join(data_home, *args)


def get_user_config_path(*args):
    if sys.platform == "win32":
        return win32_get_app_data_path(*args)

    config_home = os.environ.get(
        'XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

    return os.path.join(config_home, *args)


def win32_get_app_data_path(*args):
    shell32 = ctypes.WinDLL("shell32.dll")
    SHGetFolderPath = shell32.SHGetFolderPathW
    SHGetFolderPath.argtypes = (
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.c_wchar_p)
    SHGetFolderPath.restype = ctypes.c_uint32

    CSIDL_LOCAL_APPDATA = 0x001c
    MAX_PATH = 260

    buf = ctypes.create_unicode_buffer(MAX_PATH)
    res = SHGetFolderPath(0, CSIDL_LOCAL_APPDATA, 0, 0, buf)
    if res != 0:
        raise Exception("Could not deterime APPDATA path")

    return os.path.join(buf.value, *args)


def detect_listen_opts(address, port):
    if address is None:
        try:
            address = socket.gethostbyname(socket.gethostname())
        except socket.error:
            address = "127.0.0.1"

    if port is None:
        # test if we can use port 80
        s = socket.socket()
        port = 80
        try:
            s.bind((address, port))
            s.listen(-1)
        except socket.error:
            port = 8000
        finally:
            s.close()

    return address, port


def setup_django_environment(settings_path):
    '''
    Setup the django environment
    '''

    # Use default settings if the user didn't specify something else
    if settings_path is None:
        settings_path = get_user_config_path('wger', 'settings.py')
        print('*** No settings given, using {0}'.format(settings_path))

    # Find out file path and fine name of settings and setup django
    settings_file = os.path.basename(settings_path)
    settings_module_name = "".join(settings_file.split('.')[:-1])
    if '.' in settings_module_name:
        print("'.' is not an allowed character in the settings-file")
        sys.exit(1)
    settings_module_dir = os.path.dirname(settings_path)
    sys.path.append(settings_module_dir)
    os.environ[django.conf.ENVIRONMENT_VARIABLE] = '%s' % settings_module_name
    django.setup()


def database_exists():
    """Detect if the database exists"""

    # can't be imported in global scope as they already require
    # the settings module during import
    from django.db import DatabaseError
    from django.core.exceptions import ImproperlyConfigured
    from wger.manager.models import User

    try:
        # TODO: Use another model, the User could be deactivated
        User.objects.count()
    except DatabaseError:
        return False
    except ImproperlyConfigured:
        print("Your settings file seems broken")
        sys.exit(0)
    else:
        return True


def start_browser(url):
    '''
    Start the web browser with the given URL
    '''
    browser = webbrowser.get()

    def function():
        time.sleep(1)
        browser.open(url)

    thread = threading.Thread(target=function)
    thread.start()
