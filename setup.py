"""
NetworkBuster Setup Script
Build and install NetworkBuster as a Windows application
"""

from setuptools import setup, find_packages
import os
import sys

# Read version from config
VERSION = "1.0.1"
DESCRIPTION = "NetworkBuster - Complete Network Management Suite"
LONG_DESCRIPTION = """
NetworkBuster is a comprehensive network management suite featuring:
- Real-time network monitoring and topology mapping
- API endpoint tracing and performance analysis
- Mission control dashboard
- Audio streaming server
- Universal launcher with scheduled deployment
- Maximum power production optimization
"""

# Requirements
REQUIREMENTS = [
    'flask>=3.0.0',
    'flask-cors>=4.0.0',
    'requests>=2.31.0',
    'psutil>=5.9.0',
    'schedule>=1.2.0',
]

setup(
    name='networkbuster',
    version=VERSION,
    author='NetworkBuster Team',
    author_email='admin@networkbuster.net',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://networkbuster.net',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.14',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'networkbuster=networkbuster_launcher:main',
            'networkbuster-map=network_map_viewer:main',
            'networkbuster-tracer=api_tracer:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
