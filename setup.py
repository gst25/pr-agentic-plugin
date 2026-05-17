from setuptools import find_packages, setup

setup(
    name="agentic-plugin",
    version="0.1.0",
    description="Turn PRDs into Pull Requests — powered by AI agents",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.30.0",
        "anthropic>=0.28.0",
        "google-generativeai>=0.5.0",
        "PyGithub>=2.3.0",
        "GitPython>=3.1.43",
        "pdfplumber>=0.11.0",
        "python-dotenv>=1.0.1",
        "rich>=13.7.0",
        "pydantic>=2.7.0",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "agentic=main:main",
        ],
    },
)
