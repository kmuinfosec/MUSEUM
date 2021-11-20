from setuptools import setup, find_packages

setup_requires = [
    ]

install_requires = [
    'cycler' == '0.11.0',
    'elasticsearch' == '7.15.2',
    'kiwisolver' == '1.3.2',
    'numpy' == '1.21.4',
    'pyparsing' == '3.0.6',
    'python-dateutil' == '2.8.2',
    'six' == '1.16.0',
    'tqdm' == '4.62.3',
    'urllib3' == '1.26.7'
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
    data_files=[('museum/module', [
        'museum/module/ae_32bit_windows.dll',
        'museum/module/ae_64bit_windows.dll',
        'museum/module/ae_64bit_linux.so'
    ])]
)