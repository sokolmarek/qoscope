import setuptools
import pathlib

DESCRIPTION = """\
Qoscope is a fork of Wicope rewritten for PySide 6.3 using QML.
It's a oscilloscope app with GUI that uses Arduino for signal acquisition. 
The app was created purely for educational purposes and for electronic enthusiasts.
"""

with open("requirements_users.txt") as f:
    required_packages = f.read().splitlines()

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setuptools.setup(
    name="qoscope",
    version="1.0.0",
    author="Marek Sokol",
    author_email="mareksokol98@gmail.com",
    description="A fast Arduino Oscilloscope",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sokolmarek/qoscope",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=required_packages,
    entry_points={"console_scripts": ["qoscope = qoscope.app:main"]},
)
