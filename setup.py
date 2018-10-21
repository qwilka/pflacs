from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pflacs',
    version='0.1.0',
    description='Faster load-cases and parameter studies.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qwilka/pflacs',
    author='Stephen McEntee',
    author_email='stephenmce@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    keywords='science engineering computational productivity',
    packages=find_packages(exclude=['docs', 'examples']),
    python_requires='>=3.6',
    install_requires=[
        "vntree",
    ],
)
