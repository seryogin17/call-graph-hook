from setuptools import setup, find_packages

setup(name='pre-commit-callgraph',
      packages=['precommit'],
      include_package_data=True,
      scripts=['precommit/pre-commit-callgraph.py'],
      zip_safe=False)
