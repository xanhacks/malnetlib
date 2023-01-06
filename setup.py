from setuptools import setup, find_packages


VERSION = "1.0.1"

with open("requirements.txt", encoding="utf8") as pkg_file:
    packages = pkg_file.read().splitlines()

with open("README.md", encoding="utf8") as readme_file:
    readme_content = readme_file.read()


setup(
    name="malnetlib",
    version=VERSION,
    url="https://github.com/xanhacks/malnetlib",
    description="MalNetLib is a Python library for parsing PE files made with .NET",
    long_description=readme_content,
    long_description_content_type="text/markdown",
    keywords=["dotnet", "parser"],
    packages=find_packages(),
    install_requires=packages,
)
