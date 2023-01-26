from setuptools import setup


VERSION = "1.0.8"

with open("README.md", encoding="utf8") as readme_file:
    readme_content = readme_file.read()

setup(
    name="malnetlib",
    version=VERSION,
    author="xanhacks",
    url="https://github.com/xanhacks/malnetlib",
    description="MalNetLib is a Python library for parsing PE files made with .NET",
    long_description=readme_content,
    long_description_content_type="text/markdown",
    keywords=["dotnet", "parser"],
    install_requires=["pythonnet>=3.0.1"]
)
