from setuptools import setup

with open("README.rst") as f:
    long_description = f.read()

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
        install_requires=["monotonic==1.2",
                          "paramiko==2.0.2"],
        keywords=[],
        packages=["artisan",
                  "artisan.worker",
                  "artisan.worker.local"],
        zip_safe=False,
        classifiers=["Programming Language :: Python :: 2",
                     "Programming Language :: Python :: 2.6",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.3",
                     "Programming Language :: Python :: 3.4",
                     "Programming Language :: Python :: 3.5",
                     "Programming Language :: Python :: 3.6",
                     "License :: OSI Approved :: MIT License"]
    )
