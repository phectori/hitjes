import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hitjes-phectori", # Replace with your own username
    version="0.0.1",
    author="Frits Kuipers",
    description="Listen to the same youtube list simultaneously",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phectori/hitjes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)