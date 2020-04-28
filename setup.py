from os import path
from setuptools import setup

from yades_smtp import __version__, __author__


root_dir = path.abspath(path.dirname(__file__))

with open(path.join(root_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='yades_smtp',
    version=__version__,
    author=__author__,
    packages=['yades_smtp'],
    include_package_data=True,
    url='https://github.com/yades/yades-smtp/',
    license='MIT',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications',
        'Topic :: Communications :: Email',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='email smtp asyncio',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'yades_smtp=yades_smtp.main:main',
        ],
    },
)
