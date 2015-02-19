# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

import noseapp_daemon


with open('requirements.txt') as fp:
    requirements = [req.strip() for req in fp.readlines() if not req.startswith('--')]


if __name__ == '__main__':
    setup(
        name='noseapp_daemon',
        url='https://github.com/trifonovmixail/noseapp_daemon',
        version=noseapp_daemon.__version__,
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        description='daemon extension for noseapp lib',
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=requirements,
    )
