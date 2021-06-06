from setuptools import setup

KEYWORDS = ["logging", "structured", "structure", "log", "ecs", "apache-combined-log"]

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='structlog-extensions-nralbers',
    version='1.0.4',
    packages=['structlog_extensions'],
    url='https://structlog-extensions-nralbers.readthedocs.io/en/latest/',
    project_urls={
        'Documentation': 'https://structlog-extensions-nralbers.readthedocs.io/en/latest/',
        'Source': 'https://github.com/nralbers/structlog-extensions-nralbers',
        'Tracker': 'https://github.com/nralbers/structlog-extensions-nralbers/issues',
    },
    license='MIT',
    author='Niels Albers',
    author_email='nralbers@gmail.com',
    description='Processors for Structlog library',
    install_requires=['structlog>=19.2','user-agents','deepmerge', 'pytz'],
    keywords=KEYWORDS,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires='~=3.5',
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers"
    ],
)
