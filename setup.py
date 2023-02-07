
from setuptools import setup, find_packages

# Call setup function
setup(
    author="David Fallon",
    description="Simple space invaders style pygame.",
    name="simpsons_space_invaders",
    packages=find_packages(include=["simpsons_space_invaders",
                                    "simpsons_space_invaders.*"]),
    version="0.1.0",
)