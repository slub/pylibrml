import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylibrml",
    version="0.2.0.dev1",
    author="Thomas Baer",
    author_email="thomas.baer@slub-dresden.de",
    description="Example implementation for LibRML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slub/pylibrml",
    packages=setuptools.find_packages(include=['common', 'model', 'tmpl']),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='~=3.8',
    install_requires=['jinja2'],
)
