from Cython.Build import cythonize
from setuptools import setup, Extension

cpositionlib = Extension("cpositionlib", sources=["src/overcome/cposition/cpositionlib.pyx"])

setup(
    name='overcome',
    version='0.1.0',
    packages=['src', 'src.overcome', 'src.overcome.position'],
    url='',
    license='GPLv3+',
    author='Jaume Mila Bea',
    author_email='jaume@westial.com',
    description='Calculate the bid/ask outcome of every row in a dataframe with '
                'stock exchange candle bars data (OHLCV).',
    ext_modules=cythonize(
        [cpositionlib],
        compiler_directives={'language_level': "3"})

)