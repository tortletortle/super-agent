from setuptools import setup, find_packages

setup(
    name="super-agent",
    version="0.1.0",
    description="超级智能体框架 — 多专业 Agent 编排成超级智能体",
    author="SuperAgent Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)