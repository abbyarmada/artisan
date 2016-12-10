from setuptools import setup

with open("README.rst") as f:
    long_description = f.read()


if __name__ == "__main__":
    setup(
        name="artisan",
        description=("Providing a platform-agnostic interface for automation, "
                     "continuous integration, and farm management. "),
        long_description=long_description,
        license="MIT",
        url="https://www.github.com/SethMichaelLarson/artisan",
        version="0.0.1",
        author="Seth Michael Larson",
        author_email="sethmichaellarson@protonmail.com",
        maintainer="Seth Michael Larson",
        maintainer_email="sethmichaellarson@protonmail.com",
        install_requires=["arrow==0.10.0",
                          "enum34==1.1.6",
                          "monotonic==1.2",
                          "paramiko==2.1.0"],
        keywords=["artisan",
                  "farm",
                  "worker",
                  "ssh",
                  "automation",
                  "cli",
                  "auto",
                  "distributed",
                  "computing"],
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
