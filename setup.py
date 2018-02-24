from setuptools import setup

setup(
      name='vern-raspored',
      version='0.1',
      description='Scraps VERN studomatic and creates ics calendar with lessons',
      url='http://github.com/iprlic/VERNRaspored',
      author='iprlic',
      license='MIT',
      py_modules = ['vern-raspored'],
      install_requires=[
            'click',
            'requests[security]',
            'ics',
            'pytz',
            'lxml'
      ],
      entry_points = '''
        [console_scripts]
        vern-raspored=scrape:cli
      '''
)
