import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hitjes-phectori", # Replace with your own username
    version="0.0.2",
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
    install_requires=[
          'flask_socketio==5.0.1',
          'google-api-python-client==1.12.8',
          'eventlet==0.30.0',
          'gitpython==3.1.12',
		  'tinydb==4.3.0',
          'googleapi==0.1.0',
    ],
    python_requires='>=3.7',
)
