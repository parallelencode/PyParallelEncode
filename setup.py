import setuptools

REQUIRES = [
    'numpy',
    'scenedetect[opencv]',
    'opencv-python',
    'psutil',
    'scipy',
    'python-Levenshtein',
]

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="parallelencode",
    version="0.1.2",
    author="Parallel Encoders",
    author_email="eli.stonium@gmail.com",
    description="Cross platform framework for splitting and parallel encoding of video",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parallelencode/PyParallelEncode",
    packages=setuptools.find_packages('.'),
    install_requires=REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
