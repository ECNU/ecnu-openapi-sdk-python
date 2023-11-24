import setuptools
# encoding: utf-8

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ecnu-openapi-sdk-python",
    version="1.0.0",
    author="ECNU",
    author_email="dataservice@ecnu.edu.cn",
    description="ecnu-openapi-sdk-python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ECNU/ecnu-openapi-sdk-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "oauthlib==3.2.0",
        "psutil==5.9.4",
        "Requests==2.31.0",
        "requests_oauthlib==1.3.1",
        "SQLAlchemy==2.0.22",
        "psycopg2",
        "pymssql",
        "pymysql",
        "cx_oracle"
    ],
)