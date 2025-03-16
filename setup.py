from setuptools import setup, find_packages

setup(
    name="taxai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.105.0",
        "uvicorn>=0.23.2",
        "pydantic>=2.5.2",
    ],
)
