from setuptools import setup, find_packages

setup(
    name="nexora-control",
    version="0.1.0",
    description="Active execution guardrails, budget circuit breakers, and loop interceptors for AI agents.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="NEXORA Team",
    author_email="sirrviny@gmail.com",
    url="https://github.com/nexora-control/nexora-control",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
