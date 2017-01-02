from setuptools import setup, find_packages
import os

version = '1.0.1'

long_description = open('README.md').read()

setup(name='cyberapps.knowledge',
      version=version,
      description="loops application providing knowledge management functionality",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      author='cyberconcepts.org team',
      author_email='team@cyberconcepts.org',
      url='https://www.cyberconcepts.org',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['cyberapps'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'loops',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
