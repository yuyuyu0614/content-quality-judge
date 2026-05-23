from setuptools import setup, find_packages

setup(
    name="content-quality-judge",
    version="0.1.0",
    description="AI-powered content quality assessment — input text, get 0-1 quality score",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Estimate Project",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    keywords="ai, content-quality, fact-checking, llm, information-quality, trust",
)