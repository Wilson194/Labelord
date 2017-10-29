from setuptools import setup

with open('README') as f:
    long_description = ''.join(f.readlines())

setup(
    name='labelord_horacj10',
    version='0.3',
    description='Application for manipulation with labels at GitHub',
    long_description=long_description,
    author='Jan Horáče  k',
    author_email='horacj10@fit.cvut.cz',
    license='Public Domain',
    url='https://github.com/Wilson194/MI-PYT-DU1/',
    packages=['labelord'],
    install_requires=['Flask', 'click>=6', 'jinja2', 'requests', 'click', 'configparser'],
    entry_points={
        'console_scripts': [
            'labelord = labelord.labelord:main',
        ],
    },
    package_data={'labelord': ['templates/*.html']},
    zip_safe=False,

)
