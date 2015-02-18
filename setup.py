# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

import noseapp_daemon


if __name__ == '__main__':
    setup(
        name='noseapp_daemon',
        version=noseapp_daemon.__version__,
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        description='daemon extension for noseapp lib',
        install_requires=[
            'psutil==2.2.1',
        ],
    )
