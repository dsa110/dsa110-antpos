from setuptools import setup
from version import get_git_version

setup(name='dsa110-antpos',
      version=get_git_version(),
      url='http://github.com/dsa110/dsa110-antpos/',
      packages=['antpos'],
      package_data={
          'antpos': ['data/DSA110*.csv', 'data/ant_ids.csv']},
      zip_safe=False)

