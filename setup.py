from setuptools import setup, find_packages

setup_requires = [
    ]

install_requires = [
    'cycler==0.10.0',
    'elasticsearch==7.1.0',
    'kiwisolver==1.1.0',
    'matplotlib==3.1.2',
    'numpy==1.17.4',
    'pyparsing==2.4.5',
    'python-dateutil==2.8.1',
    'six==1.13.0',
    'tqdm==4.36.1',
    'urllib3==1.25'
]

dependency_links = [
    ]

setup(
    name='MUSEUM',
    version='1.0',
    description='Multi Feature Search Engine Using Malware Bigdata',
    author='KMU Infosec',
    author_email='m2019551@kookmin.ac.kr',
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    )