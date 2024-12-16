from setuptools import setup, find_namespace_packages

setup(
    name = 'bugal',
    version = '0.0.1',
    package=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts':[
            'bugal = bugal.ui:cli',
        ],
    },

)