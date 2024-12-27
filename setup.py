from setuptools import setup, find_packages

setup(
    name='odt_tool',
    version='1.0.0',
    description='A tool to process and edit ODT files via a web interface.',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'flask',
        'xmlstarlet',
        'lxml',
        'odfpy'
    ],
    entry_points={
        'console_scripts': [
            'odt_tool=app:main',
        ],
    },
)

