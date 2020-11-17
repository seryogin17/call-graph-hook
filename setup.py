from setuptools import setup

setup(name='callgraph',
      packages=['callgraph'],
      include_package_data=True,
      scripts=['callgraph/callgraph_wrapper.py'],
      zip_safe=False)
