from setuptools import setup, find_packages

setup(name='pre-commit-callgraph',
      setup_requires=['setuptools_scm'],
      use_scm_version=True,
      packages=['precommitcallgraph'],
      include_package_data=True,
      scripts=['scripts/pre-commit-callgraph'],
      install_requires=[
        'pandas',
        'logging'],
      zip_safe=False)
