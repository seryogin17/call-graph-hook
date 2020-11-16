from setuptools import setup, find_packages

setup(name='pre-commit-callgraph',
      packages=find_packages(),
      include_package_data=True,
      scripts=['scripts/pre-commit-callgraph'],
      zip_safe=False)
