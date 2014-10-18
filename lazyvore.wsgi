from pyramid.paster import get_app, setup_logging
from os.path import expandvars

ini_path = expandvars('$INI_PATH')
setup_logging(ini_path)
application = get_app(ini_path, 'main')
