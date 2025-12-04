from setuptools import setup, find_packages

setup(
    name='VMonViz',
    version='1.0.0',
    author='Nicholi Shiell',
    description='VM Monitoring Visualization Tool',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'matplotlib',
        'numpy',
        'rcsdb==1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'vmonviz=vmonviz.vmonviz:main',
        ],
    },
)
