from setuptools import setup, find_packages

setup(
    name="non-core-asset-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "langchain",
        "langchain-community",
        "requests",
        "beautifulsoup4",
        "selenium",
        "faiss-cpu",
        "pymysql",
        "sqlalchemy",
        "openpyxl",
        "matplotlib",
        "seaborn",
    ],
)
