from setuptools import setup, find_packages

setup_requires = [
    ]

with open('requirements.txt') as f:
    required = f.read().splitlines()

dependency_links = [
    ]

setup(
    name='museum',
    version='1.1',
    description='Multifacted Search Engine Using MinHash Sampling',
    author='KMU Infosec',
    author_email='hurjn96@kookmin.ac.kr',
    packages=find_packages(),
    install_requires=required,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    data_files=[('museum/module', [
        'museum/module/ae_32bit_windows.dll',
        'museum/module/ae_64bit_windows.dll',
        'museum/module/ae_64bit_linux.so'
    ])]
)