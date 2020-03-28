from setuptools import setup

setup(name='dsa110-antpos',
      url='http://github.com/dsa110/dsa110-antpos/',
      packages=['antpos'],
      package_data={
          'antpos': ['data/DSA110_positions_RevD.csv','data/DSA110_positions_RevE.csv','data/ant_ids.csv']},
      zip_safe=False)

