"""
setup file for degiroasync
"""
import sys
import os

import setuptools


if __name__ == '__main__':

    description_short = "No more boilerplate to check and build a Python object from JSON."

    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="jsonloader",
        version="0.4.1",
        author_email="ohmajesticlama@gmail.com",
        description=description_short,
        long_description=long_description,
        long_description_content_type='text/markdown',
        url="https://github.com/OhMajesticLama/jsonloader",
        packages=setuptools.find_packages(),
        install_requires=[
            'typeguard >= 2.13.3'
            ],
        extras_require={
            'dev': [
                'nose2 >= 0.10.0',
                'mypy >= 0.931',
                'coverage >= 6.3',
                'build >= 0.7.0'
                ]
            },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        test_suite='nose2.collector',
        tests_require=['nose2']
    )

