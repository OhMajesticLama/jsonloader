"""
setup file for degiroasync
"""
import sys
import os

import setuptools


if __name__ == '__main__':

    description_short = (
        "This module is for you if you're tired of writing boilerplate that:"
        "\n- build a straightforward Python object from loaded JSON."
        "\n- checks that your input JSON has all necessary attributes for your pipeline."
        "\n- checks that your input JSON has the right types.")

    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="jsonloader",
        version="0.4",
        author_email="ohmajesticlama@gmail.com",
        description=description_short,
        long_description=long_description,
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

