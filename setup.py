import sys
from setuptools import setup

with open("README.rst") as f:
    long_description = f.read()

install_requires = ["colorama==0.3.7",
                    "monotonic==1.2",
                    "paramiko==2.0.2"]

if sys.version_info < (3, 4):
    install_requires.append("enum34==1.1.6")

if __name__ == "__main__":
    setup(
        name="artisan",
        description=("Generalized farm management module for highly"
                     " customized build and testing pipelines."),
        long_description=long_description,
        license="MIT",
        url="https://www.github.com/SethMichaelLarson/artisan",
        version="0.1",
        author="Seth Michael Larson",
        author_email="sethmichaellarson@protonmail.com",
        maintainer="Seth Michael Larson",
        maintainer_email="sethmichaellarson@protonmail.com",
        install_requires=install_requires,
        keywords=[],
        packages=["artisan",
                  "artisan.scheduler",
                  "artisan.worker",
                  "artisan.worker.local",
                  "artisan.worker.ssh"],
        zip_safe=False,
        classifiers=["Development Status :: 2 - Pre-Alpha",
                     "Environment :: Console",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Natural Language :: English",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.3",
                     "Programming Language :: Python :: 3.4",
                     "Programming Language :: Python :: 3.5",
                     "Programming Language :: Python :: 3.6",
                     "Topic :: Scientific/Engineering :: Human Machine Interfaces",
                     "Topic :: System :: Clustering",
                     "Topic :: System :: Distributed Computing",
                     "Topic :: System :: Monitoring",
                     "Topic :: System :: Systems Administration"]
    )
