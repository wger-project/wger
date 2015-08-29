#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    wger.main
    ~~~~~~~~~

    Main script to start and set up wger Workout Manager.

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

import six
import base64
import ctypes
import optparse
import os
import socket
import sys
import tempfile
import threading
import time
import webbrowser
import inspect

import django.conf
from django.core.management import execute_from_command_line
from django.core.management import call_command

from wger import get_version


CONFIG_TEMPLATE = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wger.settings_global import *

# Use 'DEBUG = True' to get more details for server errors
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your name', 'your_email@example.com'),
)
MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%(dbengine)s',
        'NAME': %(dbname)s,
        'USER': '%(dbuser)s',
        'PASSWORD': '%(dbpassword)s',
        'HOST': '%(dbhost)s',
        'PORT': '%(dbport)s',
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = %(default_key)r

# Your reCaptcha keys
RECAPTCHA_PUBLIC_KEY = '%(recaptcha_public_key)s'
RECAPTCHA_PRIVATE_KEY = '%(recaptcha_private_key)s'
NOCAPTCHA = True

# The site's URL (e.g. http://www.my-local-gym.com or http://localhost:8000)
# This is needed for Mozilla's BrowserID to work
SITE_URL = '%(siteurl)s'
BROWSERID_AUDIENCES = [SITE_URL]

# This might be a good idea if you setup memcached
#SESSION_ENGINE = "django.contrib.sessions.backends.cache"


# Path to uploaded files
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '%(media_folder_path)s'
MEDIA_URL = SITE_URL + '/static/'
if DEBUG:
    # Serve the uploaded files like this only during development
    STATICFILES_DIRS = (MEDIA_ROOT, )
"""

KEY_LENGTH = 30

# sentinel used to signal that the database ought to be stored
# relative to the portable's directory
_portable_db_path = object()


def process_options(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = optparse.OptionParser(
        description="Run wger Workout Manager using django's builtin server")
    parser.add_option("-a", "--address", help="IP Address to listen on.")
    parser.add_option("-p", "--port", type="int", help="Port to listen on.")
    parser.add_option(
        "--syncdb", action="store_true",
        help="Update/create database before starting the server.")
    parser.add_option(
        "--reset-admin", action="store_true",
        help="Make sure the user 'admin' exists and uses 'admin' as password.")
    parser.add_option(
        "-s", "--settings", help="Path to the wger configuration file.")
    parser.add_option(
        "--no-reload", action="store_true",
        help="Do not reload the development server.")
    parser.add_option(
        "--no-browser", action="store_true",
        help="Do not open the application in a browser.")
    parser.add_option(
        "--migrate-db", action="store_true",
        help="Runs all database migrations (safe operation).")
    parser.add_option(
        "--version", action="store_true",
        help="Show version and exit.")
    parser.add_option(
        "--show-config", action="store_true",
        help="Show configuration paths and exit.")

    opts, args = parser.parse_args(argv)
    if opts.version:
        print(get_version())
        exit(0)
    if opts.show_config:
        print("Settings file: %s" % get_user_config_path('wger', 'settings.py'))
        print("Database file: %s" % get_user_data_path('wger', 'database.sqlite'))
        exit(0)
    if args:
        sys.stderr.write("This command does not take arguments!\n\n")
        parser.print_help()
        sys.exit(1)

    return opts


def main(argv=None):
    opts = process_options(argv)
    _main(opts)


def win32_portable_main(argv=None):
    """special entry point for the win32 portable version"""

    opts = process_options(argv)

    database_path = None

    if opts.settings is None:
        portable_dir = get_portable_path()
        try:
            fd, test_file = tempfile.mkstemp(dir=portable_dir)
        except OSError:
            portable_dir_writeable = False
        else:
            portable_dir_writeable = True
            os.close(fd)
            os.unlink(test_file)

        if portable_dir_writeable:
            opts.settings = os.path.join(
                portable_dir, "wger", "settings.py")
            database_path = _portable_db_path

    _main(opts, database_path=database_path)


def _main(opts, database_path=None):
    # Find the path to the settings
    settings_path = opts.settings
    if settings_path is None:
        settings_path = get_user_config_path('wger', 'settings.py')

    # Override URL if no browser should be started
    addr, port = detect_listen_opts(opts.address, opts.port)
    if opts.no_browser:
        url = None
    else:
        # Find url to wger
        if port == 80:
            url = "http://{0}".format(addr)
        else:
            url = "http://{0}:{1}".format(addr, port)

    # Create settings if necessary
    if not os.path.exists(settings_path):
        create_settings(settings_path, database_path, url)

    # Set the django environment to the settings
    setup_django_environment(settings_path)

    # Create Database if necessary
    if not database_exists() or opts.syncdb:
        run_syncdb()
        create_or_reset_admin_user()

    # Only run the south migrations
    elif opts.migrate_db:
        run_south()

    # Reset Admin
    elif opts.reset_admin:
        create_or_reset_admin_user()

    # Start wger
    if opts.no_reload:
        extra_args = ['--noreload']
    else:
        extra_args = []

    start_wger(addr, port, start_browser_url=url, extra_args=extra_args)


def create_settings(settings_path, database_path=None, url=None):
    settings_module = os.path.dirname(settings_path)
    print("* No settings file found. Creating one at %s" % settings_module)

    if database_path is _portable_db_path:
        database_path = get_portable_db_path()
        dbpath_value = 'wger.main.get_portable_db_path()'
    else:
        if database_path is None:
            database_path = get_user_data_path('wger', 'database.sqlite')
        dbpath_value = repr(fs2unicode(database_path))

    media_folder_path = get_user_data_path('wger', 'media')
    print("Please edit your settings file and enter the values for the reCaptcha keys ")
    print("You can leave this empty, but won't be able to register new users")
    recaptcha_public_key = ''
    recaptcha_private_key = ''

    # Fill in the config file template

    # The environment variable is set by travis during testing
    if os.environ.get('DB') == 'postgresql':
        dbengine = 'postgresql_psycopg2'
        dbname = "'test_wger'"
        dbuser = 'postgres'
        dbpassword = ''
        dbhost = '127.0.0.1'
        dbport = ''
    elif os.environ.get('DB') == 'mysql':
        dbengine = 'mysql'
        dbname = "'test_wger'"
        dbuser = 'root'
        dbpassword = ''
        dbhost = '127.0.0.1'
        dbport = ''
    else:
        dbengine = 'sqlite3'
        dbname = dbpath_value
        dbuser = ''
        dbpassword = ''
        dbhost = ''
        dbport = ''

    settings_content = CONFIG_TEMPLATE % dict(
        default_key=base64.b64encode(os.urandom(KEY_LENGTH)),
        dbpath=dbpath_value,
        dbengine=dbengine,
        dbname=dbname,
        dbuser=dbuser,
        dbpassword=dbpassword,
        dbhost=dbhost,
        dbport=dbport,
        siteurl=url,
        recaptcha_public_key=recaptcha_public_key,
        recaptcha_private_key=recaptcha_private_key,
        media_folder_path=media_folder_path)

    if not os.path.exists(settings_module):
        os.makedirs(settings_module)

    if not os.path.exists(os.path.dirname(database_path)):
        os.makedirs(os.path.dirname(database_path))

    with open(settings_path, 'w') as settings_file:
        settings_file.write(settings_content)


def setup_django_environment(settings_path):
    settings_file = os.path.basename(settings_path)
    settings_module_name = "".join(settings_file.split('.')[:-1])
    if '.' in settings_module_name:
        print("'.' is not an allowed character in the settings-file")
        sys.exit(1)
    settings_module_dir = os.path.dirname(settings_path)
    sys.path.append(settings_module_dir)
    os.environ[django.conf.ENVIRONMENT_VARIABLE] = '%s' % settings_module_name


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


def database_exists():
    """Detect if database exists"""

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


def init_south():
    '''
    Only perform the south initialisation
    '''
    print("* Initialising south")
    execute_from_command_line(["", "migrate", "core", "0001"])
    execute_from_command_line(["", "migrate", "exercises", "0001"])
    execute_from_command_line(["", "migrate", "config", "0001"])
    execute_from_command_line(["", "migrate", "manager", "0001"])
    execute_from_command_line(["", "migrate", "nutrition", "0001"])
    execute_from_command_line(["", "migrate", "weight", "0001"])
    execute_from_command_line(["", "migrate", "gym", "0001"])


def run_south():
    '''
    Run all south migrations
    '''
    execute_from_command_line(["", "migrate", "core"])
    execute_from_command_line(["", "migrate", "gym"])
    execute_from_command_line(["", "migrate", "config"])
    execute_from_command_line(["", "migrate", "manager"])
    execute_from_command_line(["", "migrate", "exercises"])
    execute_from_command_line(["", "migrate", "nutrition"])
    execute_from_command_line(["", "migrate", "weight"])

    # Other apps
    execute_from_command_line(["", "migrate", "easy_thumbnails"])
    execute_from_command_line(["", "migrate", "tastypie"])


def load_fixtures():
    '''
    Loads all fixtures
    '''
    os.chdir(os.path.dirname(inspect.stack()[0][1]))
    current_dir = os.getcwd()

    # Gym
    path = os.path.join(current_dir, 'gym', 'fixtures/')
    call_command("loaddata", path + "gym.json")

    # Core
    path = os.path.join(current_dir, 'core', 'fixtures/')
    call_command("loaddata", path + "languages.json")
    call_command("loaddata", path + "groups.json")
    call_command("loaddata", path + "users.json")
    call_command("loaddata", path + "licenses.json")
    call_command("loaddata", path + "days_of_week.json")

    # Config
    path = os.path.join(current_dir, 'config', 'fixtures/')
    call_command("loaddata", path + "language_config.json")
    call_command("loaddata", path + "gym_config.json")

    # Manager
    # path = os.path.join(current_dir, 'manager', 'fixtures/')

    # Exercises
    path = os.path.join(current_dir, 'exercises', 'fixtures/')
    call_command("loaddata", path + "equipment.json")
    call_command("loaddata", path + "muscles.json")
    call_command("loaddata", path + "categories.json")
    call_command("loaddata", path + "exercises.json")

    # Nutrition
    path = os.path.join(current_dir, 'nutrition', 'fixtures/')
    call_command("loaddata", path + "ingredients.json")
    call_command("loaddata", path + "weight_units.json")
    call_command("loaddata", path + "ingredient_units.json")

    # Gym
    path = os.path.join(current_dir, 'gym', 'fixtures/')
    call_command("loaddata", path + "gym.json")
    call_command("loaddata", path + "gym-config.json")
    call_command("loaddata", path + "gym-adminconfig.json")


def run_syncdb():
    '''
    Initialises a new database
    '''

    print("* Intialising the database")

    # Create the tables
    execute_from_command_line(["", "migrate"])

    # Perform the migrations
    run_south()

    # Load fixtures
    load_fixtures()


def create_or_reset_admin_user():
    # can't be imported in global scope as it already requires
    # the settings module during import
    from wger.manager.models import User
    try:
        admin = User.objects.get(username="admin")
        print("Password for user admin was reset to 'admin'")
    except User.DoesNotExist:
        print("Created default admin user")

    os.chdir(os.path.dirname(inspect.stack()[0][1]))
    current_dir = os.getcwd()
    path = os.path.join(current_dir, 'core', 'fixtures/')
    call_command("loaddata", path + "users.json")


def start_wger(addr, port, start_browser_url=None, extra_args=[]):
    argv = ["", "runserver", '--noreload'] + extra_args

    argv.append("{0}:{1}".format(addr, port))

    if start_browser_url:
        start_browser(start_browser_url)
    execute_from_command_line(argv)


def start_browser(url):
    browser = webbrowser.get()

    def f():
        time.sleep(1)
        browser.open(url)

    t = threading.Thread(target=f)
    t.start()


def fs2unicode(s):
    if isinstance(s, six.text_type):
        return s
    fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    return s.decode(fs_encoding)


def get_user_config_path(*args):
    if sys.platform == "win32":
        return win32_get_app_data_path(*args)

    config_home = os.environ.get(
        'XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

    return os.path.join(fs2unicode(config_home), *args)


def get_user_data_path(*args):
    if sys.platform == "win32":
        return win32_get_app_data_path(*args)

    data_home = os.environ.get(
        'XDG_DATA_HOME', os.path.join(
            os.path.expanduser('~'), '.local', 'share'))

    return os.path.join(fs2unicode(data_home), *args)


def get_portable_path(*args):
    # NOTE: sys.executable will be the path to wger.exe
    #       since it is essentially a small wrapper that embeds the
    #       python interpreter

    exename = os.path.basename(sys.executable).lower()
    if exename != "wger.exe":
        raise Exception(
            "Cannot determine portable path when "
            "not running as portable")

    portable_dir = fs2unicode(os.path.dirname(os.path.abspath(sys.executable)))
    return os.path.join(portable_dir, *args)


def get_portable_db_path():
    return get_portable_path('wger', 'database.sqlite')


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


if __name__ == "__main__":
    main()
