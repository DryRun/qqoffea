from setuptools import setup, find_packages

setup(
    name='qqoffea',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['coffea', 'rhalphalib', 'pandas', 'xxhash', 'scipy', 'mplhep', 'cloudpickle', 'numexpr'],
)
