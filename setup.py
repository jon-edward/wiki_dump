import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wiki_data_dump",
    version="0.1.0",
    author="jon-edward",
    author_email="arithmatlic@gmail.com",
    description="A package for traversing and downloading files from Wiki Data Dump mirrors.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jon-edward/wiki_dump",
    keywords=["wikimedia", "wiki data dumps", "wikipedia"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
    ],
    packages=setuptools.find_packages(include=["wiki_data_dump"]),
    python_requires=">=3.8",
)
