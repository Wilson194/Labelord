from setuptools import setup

with open('README') as f:
    long_description = ''.join(f.readlines())

setup(
    name='labelord_horacj10',
    version='0.4.0',
    description='Application for manipulation with labels at GitHub',
    long_description=long_description,
    author='Jan Horáček',
    author_email='horacj10@fit.cvut.cz',
    license='GNU General Public License v3.0',
    url='https://github.com/Wilson194/MI-PYT-DU1/',
    packages=['labelord'],
    install_requires=['Flask', 'click>=6', 'jinja2', 'requests', 'click', 'configparser', 'pytest'],
    entry_points={
        'console_scripts': [
            'labelord = labelord.labelord:main',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Version Control :: Git',
        'Framework :: Flask',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta'
    ],
    package_data={'labelord': ['templates/*.html']},
    zip_safe=True,
    keywords='labelord GitHub labels clone webserver flask requests',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'betamax', 'flexmock'],
    test_suite="tests",
    # summary='Application for GitHub issues labels replication'

)
