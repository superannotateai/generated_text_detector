import os
from setuptools import find_packages, setup

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, 'version.txt')) as fp:
    version = fp.read()

with open(os.path.join(dir_path, 'generated_text_detector/requirements.txt')) as fp:
    install_requires = fp.read()

setup(
    name='generated_text_detector',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires
)
