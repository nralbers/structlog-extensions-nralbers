from setuptools import setup


with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='structlog-extensions-nralbers',
    version='1.0.0',
    packages=['tests', 'structlog_extensions'],
    url='https://github.com/nralbers/structlog-extensions-nralbers',
    license='MIT',
    author='Niels Albers',
    author_email='nralbers@gmail.com',
    description='Processors for Structlog library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: System :: Logging"
    ],
)
