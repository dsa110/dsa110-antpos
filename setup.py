from setuptools import setup
from version import get_git_version

setup(name='dsa110-antpos',
      version=0.0,
      url='http://github.com/dsa110/dsa110-antpos/',
      packages=['antpos'],
      package_data={
          'antpos': ['data/DSA110_positions_*.csv', 'data/ant_ids.csv']},
      zip_safe=False)

