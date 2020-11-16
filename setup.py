from setuptools import setup, find_packages

setup(name='pre-commit-callgraph',
      setup_requires=['setuptools_scm'],
      use_scm_version=True,
      packages=['precommitcallgraph'],
      include_package_data=True,
      scripts=['scripts/pre-commit-callgraph'],
      zip_safe=False)
