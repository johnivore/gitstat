from setuptools import setup, find_packages

VERSION = '0.1'


setup(
    name='gitstat',
    version=VERSION,
    description='A simple tool to check your git repos for various changes and output a succinct summary.',
    author='John Begenisich',
    author_email='john.begenisich@outlook.com',
    url='https://gitlab.com/johnivore/gitstat',
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
    ],
    py_modules=['gitstat'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'click-default-group',
        'tqdm',
    ],
    entry_points='''
        [console_scripts]
        gitstat=gitstat:cli
    ''',
)
