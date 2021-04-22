from setuptools import setup

setup(
        name='voyager',
        version='0.9.0',
        author='Jente Vandersmissen',
        author_email='j.vandersmissen@amolf.nl',
        license='LICENSE.txt',
        description='A package for the generation of positionlists and working area files for the RAITH VOYAGER.',
        install_requires=["gdstk", "numpy", "matplotlib", "pandas"])
