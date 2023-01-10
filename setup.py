import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xerxes-protocol",
    version="0.1.4",
    author="Stanislav Rubint",
    author_email="stanislav@rubint.sk",
    description="Python implementation for xerxes-protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/metrotech-sk/xerxes-protocol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.8',
)