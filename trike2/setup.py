from setuptools import setup, find_packages

setup(
    name='trike',
    version='0.1.0',
    author='Musab',
    author_email='musabjamil3@gmail.com',
    description='A combinatorial abstract strategy game for two players.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MusabbinJamil/CI_trike',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # Add any dependencies here
    ],
)