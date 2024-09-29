from setuptools import setup, find_packages

# Updated by a script
VERSION = "0.7.0"

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='fastclasses-json',
    version=VERSION,
    packages=find_packages(exclude=('tests*',)),
    package_data={"fastclasses_json": ["py.typed"]},
    author='Daniel Golding',
    description='Quickly serialize dataclasses to and from JSON',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/cakemanny/fastclasses-json',
    project_urls={
        'Bug Tracker': 'https://github.com/cakemanny/fastclasses-json/issues'
    },
    license='MIT',
    keywords='fast dataclasses json fastclasses',
    python_requires='>=3.8',
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'mypy',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
    ],
)
