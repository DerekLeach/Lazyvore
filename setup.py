import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'docutils',
    'WebTest',
    'alembic',
    'mysql-connector-python',
    'cryptacular',
    'pycrypto',
    'deform',
    'colander',
    'ColanderAlchemy',
    ]

setup(name='Lazyvore',
      version='0.1.1',
      description='Lazyvore',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Derek Leach',
      author_email='develop@lazyvo.re',
      url='lazyvo.re',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='lazyvore',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = lazyvore:main
      [console_scripts]
      initialize_Lazyvore_db = lazyvore.scripts.initializedb:main
      """,
      )
