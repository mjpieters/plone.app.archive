from setuptools import setup, find_packages
import os

version = '0.1'

tests_require = ('collective.testcaselayer', 'Products.PloneTestCase')

setup(name='plone.app.archive',
      version=version,
      description="Archive Plone content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='archiving',
      author='Martijn Pieters',
      author_email='mj@jarn.com',
      url='https://github.com/mjpieters//plone.app.archive',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Acquisition',
          'Products.CMFCore',
          'ZODB3',
          'pytz',
          'zope.annotation',
          'zope.component',
          'zope.interface',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
