""" Packaging for fritzcollectd """

import io
import os
import re

from setuptools import setup


def read(*names, **kwargs):
    """ Read file relative to the directory where this file is located """
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def find_version(*file_paths):
    """ Get version number from file """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version('fritzcollectd.py')
URL = 'https://github.com/fetzerch/fritzcollectd'
setup(
    name='fritzcollectd',
    version=VERSION,
    py_modules=['fritzcollectd'],
    license='MIT',
    description='A collectd plugin for monitoring AVM FRITZ!Box routers',
    long_description=read('README.rst'),
    author='Christian Fetzer',
    author_email='fetzer.ch@gmail.com',
    url=URL,
    download_url='%s/archive/fritzcollectd-%s.tar.gz' % (URL, VERSION),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
    ],
    keywords='AVM FritzBox collectd',
    install_requires=[
        'fritzconnection'
    ],
)
