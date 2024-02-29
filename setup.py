
from setuptools import setup, find_packages

setup(
    name='async_api_throttler',
    version='0.1.2',
    packages=find_packages(exclude=["tests*", "local"]),
    install_requires=[],
    author='Amine Benkhouya',
    author_email='amine.benkhouya@example.com',
    description='Consume any API with no ratelimit breach, patient mode 💤',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/devamin/async-api-throttler/',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
