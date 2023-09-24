import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ontology_matching",
    version="0.0.1",
    author="Moritz Sommer",
    author_email="m.sommer@iat.rwth-aachen.de",
    description="providing an owl semantic matching service for owl-ontologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=["test", "test.*"])
)
