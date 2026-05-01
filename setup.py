from setuptools import setup, find_packages

setup(
    name="devicebox",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "confbox",
    ],
    entry_points={
        "console_scripts": [
            "devicebox=devicebox.main:main",
        ],
    },
    python_requires=">=3.10",
)
