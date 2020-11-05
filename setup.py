from setuptools import setup, find_packages
from codecs import open
import os


requirements = ['numpy',
                'mc-cnn==0.0.1',
                'pandora~=0.3',
                'nose2']


def readme():
    with open("README.md", "r", "utf-8") as f:
        return f.read()


setup(name='pandora_plugin_mc_cnn',
      version='x.y.z',
      description='Pandora plugin to create the cost volume with the neural network mc-cnn',
      long_description=readme(),
      packages=find_packages(),
      install_requires=requirements,
      entry_points="""
          [pandora.plugin]
          pandora_plugin_mc_cnn = pandora_plugin_mc_cnn.plugin_mc_cnn:MCCNN
      """,
      include_package_data=True,
      )
