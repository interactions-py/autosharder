from setuptools import setup

with open("README.md", "r", encoding="utf-8") as ld:
    long_description = ld.read()

setup(
    name="interactions-autosharder",
    version="2.0.0",
    description="Autosharder for interactions.py",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EdVraz/interactions-autosharder",
    author="EdVraz",
    author_email="edvraz12@gmail.com",
    license="MIT",
    packages=["interactions.ext.autosharder"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "discord-py-interactions>=4.2.1",
    ],
)
