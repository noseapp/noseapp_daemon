# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


__version__ = '1.0.6'


if __name__ == '__main__':
    setup(
        name='noseapp_daemon',
        url='https://github.com/trifonovmixail/noseapp_daemon',
        version=__version__,
        packages=find_packages(),
        author='Mikhail Trifonov',
        author_email='mikhail.trifonov@corp.mail.ru',
        license='GNU LGPL',
        description='noseapp extension for linux daemon testing',
        include_package_data=True,
        zip_safe=False,
        platforms='linux',
        install_requires=[
            'noseapp',
            'psutil==2.2.1',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Testing',
        ],
    )
