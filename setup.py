from setuptools import find_packages, setup

setup(
    name='EASGen',
    packages=find_packages(include=['EASGen']),
    version='0.1.0',
    description='A Python library to generate EAS SAME Audio using Raw Data',
    author='A-c0rN',
    license='ODbL-1.0',
    install_requires=['pydub'],
)

