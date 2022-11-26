from setuptools import setup, find_packages

# Updated by a script
VERSION = "0.6.1"

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
    python_requires='>=3.7',
    install_requires=[
        "typing_extensions;python_version=='3.7'"
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'mypy',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ],
)
