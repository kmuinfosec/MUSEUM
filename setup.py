from setuptools import setup, find_packages

setup_requires = [
    ]

install_requires = [
    'cycler==0.10.0',
    'elasticsearch==7.9.1',
    'kiwisolver==1.2.0',
    'numpy==1.19.2',
    'pyparsing==2.4.7',
    'python-dateutil==2.8.1',
    'six==1.15.0',
    'tqdm==4.50.0',
    'urllib3==1.26.5'
]

dependency_links = [
    ]

setup(
    name='museum',
    version='1.1',
    description='Multifacted Search Engine Using MinHash Sampling',
    author='KMU Infosec',
    author_email='hurjn96@kookmin.ac.kr',
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    data_files=[('museum/module', ['museum/module/ae_32bit.dll', 'museum/module/ae_64bit.dll'])]
)