"""
Setup module
"""
#!/usr/bin/env python
import os
import setuptools

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'README.md')), "r") as fh:
    long_description = fh.read()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt')), "r") as fh:
    requirements_raw = fh.read()
    requirements_list = requirements_raw.split('\n')
    requirements = []
    for req in requirements_list:
        if not req.strip().startswith('#') and len(req.strip()) > 0:
            requirements.append(req)

requirements_test = requirements + ['pytest']

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "VERSION")), "r") as fh:
    version = fh.read()

## Add additional files to the package
PACKAGE_DATA = {
    '': [
        'lib/sim/**/*',
        'commons/*',
        'comparator/*',
        'event/*',
        'model/*',
        'processor/*',
        'task/*'
    ],
}

setuptools.setup(
    name='tesla-ce-provider-pt-tpt-lib',
    version=version,
    description=long_description,
    author='Xavier Baro <xbaro@uoc.edu>, David Gañan <dganan@uoc.edu>, '
           'Roger Muñoz <rmunozber@uoc.edu>',
    author_email='xbaro@uoc.edu, dganan@uoc.edu, rmunozber@uoc.edu',
    url="https://github.com/tesla-ce/provider-pt-tpt-service",
    packages=['tpt'],
    package_dir={'tpt': '.'},
    long_description='long_description',
    install_requires=requirements,
    tests_require=requirements_test,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
      "Operating System :: POSIX :: Linux",
      "Framework :: Pytest"
    ],
    python_requires='>=3.6',
)
