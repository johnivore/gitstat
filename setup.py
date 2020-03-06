from setuptools import setup, find_packages

import gitstat

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='gitstat-johnivore',
    version=gitstat.VERSION,
    author='John Begenisich',
    author_email='john.begenisich@outlook.com',
    description='Succinctly display information about git repositories.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/johnivore/gitstat',
    python_requires='>=3.6',
    license='GPLv3',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Topic :: Software Development :: Version Control :: Git',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'click-default-group',
        'tqdm',
    ],
    entry_points="""
        [console_scripts]
        gitstat=gitstat.gitstat:cli
    """,
)
