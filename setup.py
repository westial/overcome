from setuptools import setup

setup(
    name='overcome',
    version='0.1.0',
    packages=['src', 'src.overcome', 'src.stack', 'src.overcome.position'],
    url='https://github.com/westial/overcome',
    license='GPLv3+',
    author='Jaume Mila Bea',
    author_email='jaume@westial.com',
    description='Calculate the potential buying and selling earnings from the '
                '"high", "low" and "close" trading history values',
    install_requires=['numpy'],
    extras_require={
        'dev': [
            'pandas',
            'behave'
        ]
    }
)
