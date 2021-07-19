from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='fastclasses-json',
    version='0.1.0-dev',
    packages=find_packages(exclude=('tests*',)),
    author='Daniel Golding',
    description='Quickly serialize dataclasses to and from JSON',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/lidatong/dataclasses-json',
    license='MIT',
    keywords='fast dataclasses json',
    python_requires='>=3.8',
    extra_require={
        'dev': [
            'pytest',
            'flake8',
            'mypy',
        ]
    },
)
