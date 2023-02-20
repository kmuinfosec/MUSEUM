from distutils.core import Extension
from setuptools import setup, find_packages

cext_mod = Extension("museum.cext", sources=['museum/module/lib/ae.cpp'])

setup(name="museum",
      version="2.0",
      packages=find_packages(),
      install_requires=[
            'cycler==0.11.0',
            'elasticsearch==8.6.2',
            'kiwisolver==1.4.4',
            'numpy==1.24.2',
            'pyparsing==3.0.9',
            'python-dateutil==2.8.2',
            'six==1.16.0',
            'tqdm==4.64.1',
            'urllib3==1.26.14',
            'Django==4.1.7'
      ],
      ext_modules=[cext_mod],
      description="Scalable and Multifaceted Search and Its Application for Binary Malware Files"
)
