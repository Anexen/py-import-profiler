import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-import-profiler",
    version="0.0.1",
    author="Anexen",
    author_email="avolk93@gmail.com",
    description="Python import profiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Anexen/py-import-profiler",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
