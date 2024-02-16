
from setuptools import setup, find_packages

long_description = open("README.md").read()

with open("./requirements.txt") as f:
      requirements = f.read().splitlines()


setup(
    name='ppmi500',
    version='0.1',
    packages=['ppmi500'],
    install_requires=[
        'pandas',
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'ppmi500 = ppmi500.main:main',
        ],
    },
)

