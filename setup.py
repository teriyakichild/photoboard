from setuptools import setup
from sys import path

path.insert(0, '.')

NAME = "photoboard"

if __name__ == "__main__":

    setup(
        name = NAME,
        version = "0.1.0",
        author = "Tony Rogers",
        author_email = "tony@tonyrogers.me",
        url = "https://github.com/teriyakichild/photoboard",
        license = 'ASL',
        packages = [NAME],
        package_dir = {NAME: NAME},
        package_data = {NAME: ['templates/*','install_helper.py']},
        description = "A decentralized group photo sharing app.",

        install_requires = ['pillow',
                            'tornado'],

        scripts = ['photoboard/install_helper.py'],
        entry_points={
            'console_scripts': [ 'photoboard = photoboard:main' ],
        }
    )

