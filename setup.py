"""
setup file for degiroasync
"""
import os

import setuptools  # type: ignore


if __name__ == '__main__':

    description_short = (
            "No more boilerplate to check and build a Python object from "
            "JSON.")

    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="jsonloader",
        version="0.9.0",
        author_email="ohmajesticlama@gmail.com",
        description=description_short,
        long_description=long_description,
        long_description_content_type='text/markdown',
        url="https://github.com/OhMajesticLama/jsonloader",
        packages=setuptools.find_packages(),
        python_requires=">=3.8.10",
        install_requires=[
            'typeguard >= 3.0.1'
            ],
        extras_require={
            'dev': [
                'pytest >= 7.0.1',
                'mypy >= 0.931',
                'coverage >= 6.3',
                'build >= 0.7.0',
                'ipython >= 8.0.1',
                'ipdb >= 0.13.9',
                'flake8 >= 4.0.1',
                'twine >= 3.8.0',
                ]
            },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ],
        tests_require=['pytest'],
    )
