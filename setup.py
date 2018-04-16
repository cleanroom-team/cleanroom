from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Package data:
    name='cleanroom',
    description='Linux system image creator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1',
    python_requires='>=3.5',
    setup_requires=['pytest-runner',],
    tests_require=['pytest',],
    url='https://gitlab.con/hunger/cleanroom',
    project_urls={
        'Source code': 'https://gitlab.com/hunger/cleanroom',
        'Code of Conduct': 'https://www.python.org/psf/codeofconduct/',
    },

    author='Tobias Hunger',
    author_email='tobias.hunger@gmail.com',

    classifiers=[
        'Development Status :: 4 - Beta'

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',

        'License :: OSI Approved :: GPL License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='Linux stateless immutable install image',

    # Contents:
    packages=find_packages(exclude=['systems', 'examples', 'docs', 'tests']),
    package_data={'cleanroom': ['commands/*.py']},
    entry_points={
        'console_scripts': [
            'cleanroom=cleanroom.main:run',
        ],
    },
)
