import os
import codecs
import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as file_:
        return file_.read()


def get_version():
    for line in read('transpeg/main.py').splitlines():
        if line.startswith('__version__'):
            return line.split("'")[1]
    raise Exception()


def install_requires():
    return read('requirements.txt').splitlines()


def long_description():
    with open('README.md', 'r') as file_:
        return file_.read()


setuptools.setup(
    name='transpeg',
    version=get_version(),
    install_requires=install_requires(),
    author='igrmk',
    author_email='igrmkx@gmail.com',
    description='Transparent JPEG emulation via SVG',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/igrmk/transpeg',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
    entry_points={'console_scripts': ['transpeg = transpeg:main']},
    test_suite='nose.collector',
    tests_require=['nose'],
)
