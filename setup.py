from setuptools import setup,find_packages

setup(
    name="YTdownload",
    version='0.1',
    py_modules=['ytdownload'],
    install_requires=['pytube','typer',],
    entry_points='''
    [console_scripts]
    ytdownload=ytdownload:main
    
    '''
)