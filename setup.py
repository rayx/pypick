import setuptools
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        # Disable screen capturing because it doesn't work with
        # text-based UI
        self.test_args = ['-s']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='pypick',
    version='0.2.1',
    author='Huan Xiong',
    author_email='huan.xiong@outlook.com',
    description=('A module for selecting an item from a multi-field '
                 'data list in terminal'),
    packages=['pypick'],
    url='https://github.com/rayx/pypick',
    license='GPLv3+',
    platforms='unix-like',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['urwid>=1.3.1',
                      'wcwidth'],
    tests_require=['pytest',
                   'flake8'],
    test_suite='tests',
    cmdclass={'test': PyTest},
    include_package_data=True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'])
